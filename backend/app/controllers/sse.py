import json
import asyncio
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.schemas.sse import SseRequest
from app.utils.rag import generater_response


router = APIRouter()

@router.post("/sse")
async def sse(args: SseRequest):

    async def stream():

        question = args.question

        async for chunk in generater_response(question):
            yield json.dumps({"data": chunk})
        
        yield json.dumps({"data": "END"})

    return EventSourceResponse(stream())