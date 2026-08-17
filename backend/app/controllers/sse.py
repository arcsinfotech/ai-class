import json
import asyncio
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.schemas.sse import SseRequest

router = APIRouter()

@router.post("/sse")
async def sse(args: SseRequest):

    async def stream():

        question = args.question

        # here we will implement AI part later

        answer = "Hello there! How can I help you today? I am a chatbot created by the team at AI.com to help you with your questions. Is there anything specific you would like to know?"        

        for word in answer.split(" "):
            yield json.dumps({"data": word+" "})
            await asyncio.sleep(0.1)
        
        yield json.dumps({"data": "END"})

    return EventSourceResponse(stream())