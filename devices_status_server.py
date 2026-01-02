import asyncio
import json
import logging
from time import sleep
from typing import AsyncGenerator

import uvicorn

import fastapi
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from owrx_devices_staus import owrx_devices_status

logging.basicConfig(level=logging.INFO)

app = fastapi.FastAPI()
app.add_middleware( # CORS
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )


active_connections_queues: list[asyncio.queues.Queue] = []

latest_message = None

app.mount("/devices-static", StaticFiles(directory="devices-static"), name="devices-static")


def devices_staus_change_listener(message: dict[str, str]) -> None:
    global latest_message
    latest_message = message
    logging.info(f"Received message: {latest_message}")
    # Broadcast the message to all connected clients
    for connection_queue in active_connections_queues:
        connection_queue.put_nowait(latest_message)


async def _event_stream(request: Request, queue: asyncio.queues.Queue) -> AsyncGenerator[str, None]:
    try:
        # Send the latest message to the newly connected client
        if latest_message:
            sleep(3)
            yield f"data: {json.dumps(latest_message)}\n\n"

        while True:
            if await request.is_disconnected():
                logging.info("Devices status: Client disconnected")
                break
            try:
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(message)}\n\n"
            except asyncio.TimeoutError:
                # Send last message like a ping message if no other message was sent in the last 30 seconds
                yield f"data: {json.dumps(latest_message)}\n\n"
                # yield f"data: ping\n\n"
                logging.info("Devices status: Sent last message like ping to keep connection alive")
    except asyncio.CancelledError:
        logging.info("Devices status: Event stream cancelled")
        raise
    finally:
        if queue in active_connections_queues:
            active_connections_queues.remove(queue)
        logging.info(f"Devices status: Client disconnected, active connections: {len(active_connections_queues)}")
        if len(active_connections_queues) == 0:
            no_more_client_connected()



async def push_devices_events(request: Request):
    queue: asyncio.queues.Queue = asyncio.Queue()
    active_connections_queues.append(queue)
    logging.info(f"Devices status: Client connected, active connections: {len(active_connections_queues)}")

    response = StreamingResponse(_event_stream(request, queue), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


def no_more_client_connected():
    logging.info("Devices status: No more clients connected")


@app.get("/devicesEvents")
async def devices_events(request: Request):
    return await push_devices_events(request)


if __name__ == "__main__":
    logging.info(f"Devices status server version: 1.0")
    # signal.signal(signal.SIGTERM, lambda sig, frame: app.on_shutdown())
    # signal.signal(signal.SIGINT, lambda sig, frame: app.on_shutdown())
    owrx_devices_status.set_devices_status_change_listener(devices_staus_change_listener)
    with owrx_devices_status as devices_status:
        latest_message = devices_status.prepare_massage_to_send()
        uvicorn.run(app, host="0.0.0.0", port=8000)
