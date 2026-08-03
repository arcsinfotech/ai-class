import asyncio
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

async def get_message():
    return "Hello, World!"

async def get_streaming_messages():

    yield {"data": "This is a test message"}
    await asyncio.sleep(5)    
    yield {"data": "This is the final message 2"}


@router.get("/sse")
async def sse():

    async def stream():
        message = await get_message()
        yield f"data: {message}"
        
        async for chunk in get_streaming_messages():
            yield {"data": chunk}


    return EventSourceResponse(stream())