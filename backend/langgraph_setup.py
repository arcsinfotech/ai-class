import re
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
@tool
def add(a: float, b: float) -> str:
    """Add two numbers."""
    print(f"Adding {a} and {b} in tool call")
    return a + b

TOOLS = [add]

def agent_node(state: State) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", api_key="").bind_tools(TOOLS)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def build_graph():

    builder = StateGraph(State)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(TOOLS))

    builder.add_edge(START, "agent")

    builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=MemorySaver())

def run(graph, question: str):
    config = {
        "configurable": {
            "thread_id": "123"
        }
    }

    for update in graph.stream({"messages": [HumanMessage(content=question)]}, config=config, stream_mode="updates"):
        for node_name, output in update.items():
            msg = output["messages"][-1]
            if getattr(msg, "tool_calls", None):
                print(f"  [{node_name}] tool call -> {msg.tool_calls[0]['name']}({msg.tool_calls[0]['args']})")
            else:
                print(f" [{node_name}] {msg.content}")


if __name__ == "__main__":
    graph = build_graph()

    run(graph, "What is 12 + 13? Use the add tool.")

    print(graph.get_graph().draw_mermaid())
