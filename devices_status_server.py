import asyncio
import json
import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from owrx_devices_status import owrx_devices_status

logging.basicConfig(level=logging.INFO)

logging.info("Devices status server version: 1.0")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections: list[asyncio.Queue] = []
latest_message = None

app.mount("/devices-static", StaticFiles(directory="devices-static"), name="devices-static")


def devices_status_change_listener(message: dict[str, str]) -> None:
    global latest_message
    latest_message = message
    logging.info(f"Received message: {latest_message}")
    for queue in active_connections:
        queue.put_nowait(latest_message)


async def event_stream(request: Request, queue: asyncio.Queue):
    try:
        if latest_message:
            await asyncio.sleep(3)
            yield f"data: {json.dumps(latest_message)}\n\n"

        while True:
            if await request.is_disconnected():
                break
            try:
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(message)}\n\n"
            except asyncio.TimeoutError:
                yield f"data: {json.dumps(latest_message)}\n\n"
                logging.info("Ping sent for keep alive")
    finally:
        if queue in active_connections:
            active_connections.remove(queue)
        logging.info(f"Client disconnected, active connections: {len(active_connections)}")
        if not active_connections:
            logging.info("No client connected")


@app.get("/devicesEvents")
async def devices_events(request: Request):
    queue = asyncio.Queue()
    active_connections.append(queue)
    logging.info(f"Client connected, active connections: {len(active_connections)}")
    response = StreamingResponse(event_stream(request, queue), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == "__main__":
    owrx_devices_status.set_devices_status_change_listener(devices_status_change_listener)
    with owrx_devices_status as devices_status:
        latest_message = devices_status.prepare_massage_to_send()
        uvicorn.run(app, host="0.0.0.0", port=8000)
