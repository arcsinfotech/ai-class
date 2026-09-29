import os
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

os.environ.setdefault("OPENAI_API_KEY", "")


async def main():
    client = MultiServerMCPClient({
        # "langchain_docs": {
        #     "url": "https://docs.langchain.com/mcp",
        #     "transport": "streamable_http",
        # }
        "my_mcp_server": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "sse"
        }
    })

    tools = await client.get_tools()

    print(f"Loaded {len(tools)} tool(s): {[t.name for t in tools]}\n")

    agent = create_agent("gpt-4o-mini", tools=tools)

    QUESTION = "call get_ai_class_data tool with the query: 'What is python?'"

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": QUESTION}]}
    )

    print("Final answer:\n")
    print(response)
    print("=======================================================")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())