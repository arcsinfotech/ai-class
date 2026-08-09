import asyncio
import json

from fastapi import APIRouter
from fastapi.websockets import WebSocket

router = APIRouter()

SUPPORTED_DATA_TYPES = ["stocks", "options", "money", "END"]


async def fetch_stocks_data(websocket: WebSocket):
    
    await websocket.send_text(json.dumps({"data": "stocks data"}))
    await asyncio.sleep(5)
    await websocket.send_text(json.dumps({"data": "stocks data 2"}))
    await asyncio.sleep(5)
    await websocket.send_text(json.dumps({"data": "stocks data 3"}))
    await asyncio.sleep(5)
    await websocket.send_text(json.dumps({"data": "stocks data 4"}))
    await asyncio.sleep(5)

async def fetch_options_data(websocket: WebSocket):
    await websocket.send_text(json.dumps({"data": "options data"}))
    await asyncio.sleep(5)
    await websocket.send_text(json.dumps({"data": "options data 2"}))
    await asyncio.sleep(5)
    await websocket.send_text(json.dumps({"data": "options data 3"}))
    await asyncio.sleep(5)
    await websocket.send_text(json.dumps({"data": "options data 4"}))
    await asyncio.sleep(5)

@router.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()

    while True:

        payload = await websocket.receive_text()

        json_payload = json.loads(payload)

        type_of_data = json_payload.get("type_of_data")

        if type_of_data not in SUPPORTED_DATA_TYPES:
            await websocket.send_text(json.dumps({"error": "Invalid data type"}))
            continue

        if type_of_data == "stocks":
            await websocket.send_text(json.dumps({"data": "successfully joined the stocks channel"}))
            await fetch_stocks_data(websocket)
            continue

        if type_of_data == "options":
            await websocket.send_text(json.dumps({"data": "successfully joined the  options channel"}))
            await fetch_options_data(websocket)
            continue

        if type_of_data == "END":
            await websocket.close()
            break

