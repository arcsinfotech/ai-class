import os
import random
import sqlite3
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from langchain.agents import create_agent
from langchain_core.tools import tool
from app.configs.settings import settings

CHART_DIR = os.path.join(os.getcwd(), "charts")

def build_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute(
        "CREATE TABLE sales (id INTEGER PRIMARY KEY, month TEXT, region TEXT, product TEXT, units INTEGER, revenue REAL)"
    )
    random.seed(42)
    regions = ["North", "South", "East", "West"]
    prices = {"Laptop": 900, "Phone": 600, "Tablet": 350, "Headphones": 120}
    rows =[]
    for i in range(12):
        month = f"2025-{i+1:02d}"
        for region in regions:
            for product, price in prices.items():
                units = int(random.randint(5,40) * (1+i *0.05))
                revenue = round(units * price * random.uniform(0.9,1.1), 2)
                rows.append((month, region, product, units, revenue))
    conn.executemany(
        "INSERT INTO sales (month, region, product, units, revenue) VALUES (?,?,?,?,?)", rows
    )
    conn.commit()
    return conn

conn = build_db()

def get_schema() -> str:
    rows = conn.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
    return "\n".join(r[0] for r in rows)

@tool
def run_sql(query: str) -> str:
    """Run a read-only SQL SELECT query on the sales database and return the rows."""
    if not query.strip().lower().startswith("select"):
        return "ERROR: only SELECT queries are allowed."
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        return F"ERROR: {e}. Check the schema and try again."
    if df.empty:
        return "(query returned no rows)"
    return df.head(50).to_string(index=False)

@tool
def create_graph(python_code: str, filename: str = "chart.png") -> str:
    """Run matplotlib Python code (given as a string) and save the figure as a PNG.

    In your code these are already available: plt (matplotlib.pyplot), pd (pandas),
    and query(sql) which runs a SELECT on the sales database and returns a DataFrame.
    Do NOT call plt.show() or plt.savefig() - the tool saves the figure for you.
    Always add a title and axis labels. filename must end with .png.
    """
    os.makedirs(CHART_DIR, exist_ok=True)
    path = os.path.join(CHART_DIR, os.path.basename(filename))

    scope = {"plt": plt, "pd": pd, "query": lambda sql: pd.read_sql_query(sql, conn)}
    try:
        exec(python_code, scope)
        plt.savefig(path, dpi=120, bbox_inches="tight")
    except Exception as e:
        plt.close("all")
        return f"ERROR in chart code: {type(e).__name__}: {e}. Fix the code and call create_grahp again."
    plt.close("all")
    return f"Chart saved at: {path}"



MODEL = "gpt-4o-mini"
TOOLS = [run_sql, create_graph]
SYSTEM_PROMPT = f"""You are a data analyst agent with access to a SQL database (SQLite).

Database schema:
{get_schema()}

Notes: month looks like '2025-01'. revenue is in dollars.

Rules:
- To answer data questions, write a SQL SELECT and call run_sql. Never invent numbers.
- If run_sql returns an ERROR, read it, fix the query and retry.
- Only draw a graph when the user asks (e.g. "graph it", "plot", "chart").
  "graph it" means: chart the data from the most recent answer.
- To draw, write matplotlib code as a string and call create_graph.
  Inside the code use query("SELECT ...") to load data into a DataFrame.
- After create_graph succeeds, tell the user to open the .png file (give the path).
- If create_graph returns an ERROR, fix your code and try again.
- Keep answers short and clear
"""

agent = create_agent(MODEL, tools=TOOLS, system_prompt=SYSTEM_PROMPT)

def show_trace(new_messages: list) -> None:
    for msg in new_messages:
        for call in getattr(msg, "tool_calls", None) or []:
            args = call["args"]
            if call["name"] == "run_sql":
                print(f"\n [tool: run_sql]\n SQL: {args.get('query')}")
            elif call["name"] == "create_graph":
                print(f"\n [tool: create_graph] -> {args.get('filename', 'chart.png')}")
                for line in args.get("python_code", "").splitlines():
                    print(f"    | {line}")
        # if msg.__class__.__name__ == "ToolMessages":
        #     preview = str(msg.content)
        #     print(f" [tool result]\n {}")

def analyst_agent(history: list) -> list:
    response = agent.invoke({"messages": history})
    show_trace(response['messages'][len(history):])
    print(f"\nAgent: {response['messages'][-1].content}\n")
    return response["messages"]

if __name__ == "__main__":
    conversations: list = []
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "end"]:
            break
        if user_input:
            conversations.append({"role": "user", "content": user_input})
            conversations = analyst_agent(conversations)