import json
import asyncio
from openai import OpenAI
from typing import AsyncGenerator

from app.configs.settings import settings

from sqlalchemy import text
from app.models.connection import get_async_db

SYSTEM_PROMPT = (
    "You are a helpful assistant. You have access to a `retrieve_context` tool "
    "that searches a knowledge base. Use it only when the user's question requires "
    "specific information you don't already know. Otherwise, answer directly. "
    "When you do call the tool, pass a standalone, self-contained question as the "
    "query - rewrite it using the conversation so far if the user's message relies "
    "on earlier context (e.g. pronouns, follow-ups)."
	"retrieved content also has numaric id so always while answering the question use the id to refer the content"
)


TOOLS = [
   {
      "type": "function",
      "function": {
        "name": "retrieve_context",
        "description":(
                "Search the knowledge base for relevant context to help answer the "
                "user's question. Use this whenever the question needs specific "
                "information from the documents rather than general knowledge."
        ),
        "parameters": {
           "type": "object",
           "properties": {
              "query": {
                "type": "string",
                "description": (
                        "A standalone, self-contained question capturing what the "
                        "user wants to know. Rewrite it from conversation context "
                        "if the original message depends on prior turns."
                )
              }
           },
           "required": ["query"]
        }
      }
   }
]

def embed_text(query: str, client: OpenAI) -> list[float]:
	response = client.embeddings.create(model="text-embedding-3-small", input=query, dimensions=512)
	return response.data[0].embedding  


async def retrieve_context(query: str, client: OpenAI, top_k: int = 5, index_name: str = "file_pdf") -> str:

	query_embeddings = embed_text(query, client)
	embedding_str = "[" + ",".join(str(x) for x in query_embeddings) + "]"

	async with get_async_db() as db:
		result = await db.execute(
			text("""
				SELECT content, embedding <=> CAST(:query_embedding AS vector) AS distance
				FROM vectors
				WHERE index_name = :index_name
				ORDER BY embedding <=> CAST(:query_embedding AS vector)
				LIMIT :top_k
			"""),
			{"query_embedding": embedding_str, "index_name": index_name, "top_k": top_k}
		)
		row = result.fetchall()

		if not row:
			return "No relevant context found in the knowledge base."
		
		return "\n\n".join(f"[{i +1}] {row.content}" for i, row in enumerate(row))



async def generater_response(question: str, index_name: str = "file_pdf", top_k: int = 5, conversation_history: list[dict] | None = None) -> AsyncGenerator[str, None]:
   
	messages = [
		{"role": "system", "content": SYSTEM_PROMPT},
		{"role": "user", "content": question}
	]

	client = OpenAI(api_key=settings.OPENAI_API_KEY)

	decision = client.chat.completions.create(
		model="gpt-4o-mini",
		messages=messages,
		tools=TOOLS,
		tool_choice="auto"
	)

	choice = decision.choices[0]
	tool_calls = choice.message.tool_calls


	if not tool_calls:
		if choice.message.content:
			yield choice.message.content
		return
	

	messages.append(choice.message)
     
	for tool_call in tool_calls:
		if tool_call.function.name == "retrieve_context":
			args = json.loads(tool_call.function.arguments)
			standalone_query = args["query"]
            
			context = await retrieve_context(standalone_query, client, top_k, index_name)
            
			messages.append({
				"role": "tool",
				"tool_call_id": tool_call.id,
				"content": context
			})

	stream = client.chat.completions.create(
		model="gpt-4o-mini",
		messages=messages,
		stream=True
	)

	for chunk in stream:
		delta = chunk.choices[0].delta.content
		if delta:
			yield delta
