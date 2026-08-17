import asyncio
import json

from fastapi import APIRouter
from fastapi.websockets import WebSocket

router = APIRouter()

@router.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()

    try:

        while True:

            payload = await websocket.receive_text()

            json_payload = json.loads(payload)

            question = json_payload.get("question")

            # Here we will implement AI part later

            answer = "Hello there! How can I help you today? I am a chatbot created by the team at AI.com to help you with your questions. Is there anything specific you would like to know?"        

            for word in answer.split(" "):
                await websocket.send_text(json.dumps({"data": word+" "}))
                await asyncio.sleep(0.1)

            await websocket.send_text(json.dumps({"data": "END"}))
            break
    
    except Exception as e:
        print(f"Eror: {e}")
    finally:
        await websocket.close()