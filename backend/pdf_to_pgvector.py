import asyncio
import tiktoken

from pypdf import PdfReader

from openai import OpenAI
from sqlalchemy import text
from app.models.connection import get_async_db

PATH = "file.pdf"
INDEX_NAME = "file_pdf"
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50

openai_client = OpenAI(api_key="")
tokenizer = tiktoken.encoding_for_model(EMBEDDING_MODEL)

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return full_text

def chunk_by_tokens(text_content: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    tokens = tokenizer.encode(text_content)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(tokenizer.decode(chunk_tokens))
        start += chunk_size -overlap 

    return chunks

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=chunks,
        dimensions=512
    )

    return [item.embedding for item in response.data]

async def store_vectors(chunks: list[str], embeddings: list[list[float]], index_name: str):
    async with get_async_db() as db:
        for chunk, embedding in zip(chunks, embeddings):
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
            await db.execute(
                text(
                    """
                    INSERT INTO vectors (index_name, content, embedding)
                    VALUES (:index_name, :content, CAST(:embedding AS vector))
                """),
                {
                    "index_name": index_name,
                    "content": chunk,
                    "embedding": embedding_str,
                }
            )
        
        await db.commit()
    print("Vectors stored successfully")

async def main():

    raw_text = extract_text_from_pdf(PATH)

    print(len(raw_text))

    chunks = chunk_by_tokens(raw_text, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)

    print(len(chunks))

    embeddings = embed_chunks(chunks)

    print(len(embeddings))
    print(len(embeddings[0]))

    await store_vectors(chunks, embeddings, INDEX_NAME)


if __name__ == "__main__":
    asyncio.run(main())


# CREATE TABLE vectors (
#     id          SERIAL PRIMARY KEY,
#     index_name  VARCHAR(255) NOT NULL,
#     content     TEXT NOT NULL,
#     embedding   vector(512) NOT NULL,
#     created_at  TIMESTAMP DEFAULT NOW()
# );