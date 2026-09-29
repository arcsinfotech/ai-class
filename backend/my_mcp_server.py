from fastmcp import FastMCP
from langchain_openai.chat_models import ChatOpenAI
from app.models.connection import get_async_db
from openai import OpenAI
from sqlalchemy import text

mcp = FastMCP("My Custom MCP Server")

openai_client = OpenAI(api_key="")

def embed_query(query: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
        dimensions=512
    )

    return response.data[0].embedding

@mcp.tool()
def get_ai_class_data(query: str) -> str:
    print(f"Query: {query}")
    llm = ChatOpenAI(model="gpt-4o-mini", api_key="")
    response = llm.invoke(query)
    return response.content

@mcp.tool()
async def similarity_search(query: str) -> str:
    query_embedding = embed_query(query)

    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    async with get_async_db() as db:
        result = await db.execute(
            text(
                """
                SELECT id, index_name, content, embedding <=> CAST(:query_embedding AS vector) as distance
                FROM vectors
                ORDER by embedding <=> CAST(:query_embedding AS vector)
                LIMIT 5
            """),
            {"query_embedding": embedding_str}
        )
        rows = result.fetchall()
        final_result = "\n".join([f"ID: {row[0]}, Index: {row[1]}, Content: {row[2]}, Distance: {row[3]}" for row in rows])
        print(final_result)
        return final_result

if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000, path="/mcp")