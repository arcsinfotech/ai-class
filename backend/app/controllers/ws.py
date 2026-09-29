import asyncio
import json

from fastapi import APIRouter
from fastapi.websockets import WebSocket
from app.utils.rag import generater_response

router = APIRouter()

@router.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()

    try:

        while True:

            payload = await websocket.receive_text()

            json_payload = json.loads(payload)

            question = json_payload.get("question")

            async for chunk in generater_response(question):
                await websocket.send_text(json.dumps({"data": chunk}))

            await websocket.send_text(json.dumps({"data": "END"}))
            break
    
    except Exception as e:
        print(f"Eror: {e}")
    finally:
        await websocket.close()