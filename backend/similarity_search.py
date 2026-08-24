import asyncio

from openai import OpenAI
from sqlalchemy import text

from app.models.connection import get_async_db

EMBEDDING_MODEL = "text-embedding-3-small"
INDEX_NAME = "file_pdf"

openai_client = OpenAI(api_key="")

def embed_query(query:str) -> list[float]:
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
        dimensions=512
    )

    return response.data[0].embedding

async def similarity_search(query:str, top_k: int = 5, index_name: str | None = None ):
    query_embedding = embed_query(query)

    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    async with get_async_db() as db:
        if index_name:
            result = await db.execute(
                text(
                    """
                    SELECT id, index_name, content, embedding <=> CAST(:query_embedding AS vector) as distance
                    FROM vectors
                    WHERE index_name = :index_name
                    ORDER by embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :top_k
                """),
                {"query_embedding": embedding_str, "index_name": index_name, "top_k": top_k}
            )
        else:
             result = await db.execute(
                text(
                    """
                    SELECT id, index_name, content, embedding <=> CAST(:query_embedding AS vector) as distance
                    FROM vectors
                    ORDER by embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :top_k
                """),
                {"query_embedding": embedding_str, "top_k": top_k}
            )
        
        rows = result.fetchall()
        return rows


async def main():
    query = "autonomous learner is “one who has independent capacity to make and carry out"
    rows = await similarity_search(query, top_k=5, index_name=INDEX_NAME)

    for row in rows:
        print(f"distance: {row.distance:.4f}, SCORE: {1 - row.distance:.4f} ID: {row.id}, Index: {row.index_name}")
        print(row.content[:200])
        print("-------------------------------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())