import asyncio
import json
import logging
import signal
from time import sleep
from typing import AsyncGenerator

import uvicorn

import fastapi
from starlette.requests import Request
from starlette.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from owrx_devices_staus import OwrxDevicesStatus, owrx_devices_status

logging.basicConfig(level=logging.INFO)

app = fastapi.FastAPI()

active_connections_queues: list[asyncio.queues.Queue] = []

latest_message = None

app.mount("/devices-static", StaticFiles(directory="devices-static"), name="devices-static")

# https://owrx2.fustinoni.net/status.json

# {"receiver": {"name": "<font color='black'  style='background-color: rgba(255, 255, 255, 0.5);'>  IK2ZSH </font>", "admin": "example@example.com", "gps": {"lat": 45.7007212405664, "lon": 9.65270348173823}, "asl": 300, "location": "<font color='black'  style='background-color: rgba(255, 255, 255, 0.5);'>  Bergamo, Bg, Italy  </font>"}, "max_clients": 5, "version": "v1.2.103", "sdrs": [{"name": "RTL-SDR v4", "type": "RtlSdrSource", "profiles": [{"name": "439.200 MHz", "center_freq": 439200000, "sample_rate": 2400000}, {"name": "437.200 MHz", "center_freq": 437200000, "sample_rate": 2400000}, {"name": "435.200 MHz", "center_freq": 435200000, "sample_rate": 2400000}, {"name": "433.200 MHz", "center_freq": 433200000, "sample_rate": 2400000}, {"name": "431.200 MHz - 70cm Repeaters", "center_freq": 431200000, "sample_rate": 2400000}, {"name": "145 MHz 2m", "center_freq": 145000000, "sample_rate": 2400000}, {"name": "29.5 MHz", "center_freq": 29500000, "sample_rate": 2400000}, {"name": "29.5 MHz vert 11m 1/4\u03bb", "center_freq": 29500000, "sample_rate": 2400000}, {"name": "27.5 MHz", "center_freq": 27500000, "sample_rate": 2400000}, {"name": "27.5 MHz  vert 11m 1/4\u03bb", "center_freq": 27500000, "sample_rate": 2400000}, {"name": "25.5 MHz", "center_freq": 25500000, "sample_rate": 2400000}, {"name": "25.5 MHz  vert 11m 1/4\u03bb", "center_freq": 25500000, "sample_rate": 2400000}, {"name": "23.5 MHz", "center_freq": 23500000, "sample_rate": 2400000}, {"name": "21.5 MHz", "center_freq": 21500000, "sample_rate": 2400000}, {"name": "19.5 MHz", "center_freq": 19500000, "sample_rate": 2400000}, {"name": "17.5 MHz", "center_freq": 17500000, "sample_rate": 2400000}, {"name": "15.5 MHz", "center_freq": 15500000, "sample_rate": 2400000}, {"name": "13.5 MHz", "center_freq": 13500000, "sample_rate": 2400000}, {"name": "11.5 MHz", "center_freq": 11500000, "sample_rate": 2400000}, {"name": "9.5 MHz", "center_freq": 9500000, "sample_rate": 2400000}, {"name": "7.5 MHz", "center_freq": 7500000, "sample_rate": 2400000}, {"name": "5.5 MHz", "center_freq": 5500000, "sample_rate": 2400000}, {"name": "3.5 MHz", "center_freq": 3500000, "sample_rate": 2400000}, {"name": "1.5 MHz", "center_freq": 1500000, "sample_rate": 2400000}, {"name": "137.0 MHz", "center_freq": 137000000, "sample_rate": 2400000}, {"name": "135.0 MHz", "center_freq": 135000000, "sample_rate": 2400000}, {"name": "133.0 MHz", "center_freq": 133000000, "sample_rate": 2400000}, {"name": "131.0 MHz", "center_freq": 131000000, "sample_rate": 2400000}, {"name": "129.0 MHz", "center_freq": 129000000, "sample_rate": 2400000}, {"name": "127.0 MHz", "center_freq": 127000000, "sample_rate": 2400000}, {"name": "125.0 MHz", "center_freq": 125000000, "sample_rate": 2400000}, {"name": "123.0 MHz", "center_freq": 123000000, "sample_rate": 2400000}, {"name": "121.0 MHz", "center_freq": 121000000, "sample_rate": 2400000}, {"name": "119.0 MHz", "center_freq": 119000000, "sample_rate": 2400000}, {"name": "1090MHz ADSB", "center_freq": 1090000000, "sample_rate": 2400000}, {"name": "ISM 433", "center_freq": 433900000, "sample_rate": 2400000}, {"name": "PMR", "center_freq": 446000000, "sample_rate": 2400000}, {"name": "PMR 433,600", "center_freq": 433600000, "sample_rate": 2600000}, {"name": "40.680 MHz - 8m", "center_freq": 40680000, "sample_rate": 1800000}]}, {"name": "SDRPlay", "type": "SdrplaySource", "profiles": [{"name": "10m", "center_freq": 28850000, "sample_rate": 2000000}, {"name": "11m CB", "center_freq": 27000000, "sample_rate": 2000000}, {"name": "12m", "center_freq": 24940000, "sample_rate": 250000}, {"name": "15m", "center_freq": 21225000, "sample_rate": 500000}, {"name": "17m", "center_freq": 18118000, "sample_rate": 250000}, {"name": "20m", "center_freq": 14175000, "sample_rate": 500000}, {"name": "30m", "center_freq": 10125000, "sample_rate": 250000}, {"name": "40m", "center_freq": 7150000, "sample_rate": 500000}, {"name": "60m", "center_freq": 5350000, "sample_rate": 250000}, {"name": "80m", "center_freq": 3750000, "sample_rate": 500000}, {"name": "160m", "center_freq": 1900000, "sample_rate": 250000}, {"name": "AM Broadcast", "center_freq": 1100000, "sample_rate": 2000000}, {"name": "49m Broadcast", "center_freq": 6050000, "sample_rate": 500000}, {"name": "41m Broadcast", "center_freq": 7325000, "sample_rate": 250000}, {"name": "31m Broadcast", "center_freq": 9650000, "sample_rate": 500000}, {"name": "25m Broadcast", "center_freq": 11850000, "sample_rate": 500000}, {"name": "22m Broadcast", "center_freq": 13720000, "sample_rate": 500000}, {"name": "433MHz ISM", "center_freq": 433000000, "sample_rate": 2000000}, {"name": "1090MHz ADSB", "center_freq": 1090000000, "sample_rate": 4000000}, {"name": "2m", "center_freq": 145000000, "sample_rate": 5000000}, {"name": "30-40m", "center_freq": 8500000, "sample_rate": 4000000}]}, {"name": "Nooelec sdr", "type": "RtlSdrSource", "profiles": [{"name": "437.200 MHz", "center_freq": 437200000, "sample_rate": 2400000}, {"name": "435.200 MHz", "center_freq": 435200000, "sample_rate": 2400000}, {"name": "433.200 MHz", "center_freq": 433200000, "sample_rate": 2400000}, {"name": "431.200 MHz - 70cm Repeaters", "center_freq": 431200000, "sample_rate": 2400000}, {"name": "145 MHz 2m", "center_freq": 145000000, "sample_rate": 2400000}, {"name": "53.58 MHz", "center_freq": 52800000, "sample_rate": 2400000}, {"name": "51.0 MHz", "center_freq": 51000000, "sample_rate": 2400000}, {"name": "29.5 MHz", "center_freq": 29500000, "sample_rate": 2400000}, {"name": "27.5 MHz", "center_freq": 27500000, "sample_rate": 2400000}, {"name": "137.0 MHz", "center_freq": 137000000, "sample_rate": 2400000}, {"name": "135.0 MHz", "center_freq": 135000000, "sample_rate": 2400000}, {"name": "133.0 MHz", "center_freq": 133000000, "sample_rate": 2400000}, {"name": "131.0 MHz", "center_freq": 131000000, "sample_rate": 2400000}, {"name": "129.0 MHz", "center_freq": 129000000, "sample_rate": 2400000}, {"name": "127.0 MHz", "center_freq": 127000000, "sample_rate": 2400000}, {"name": "125.0 MHz", "center_freq": 125000000, "sample_rate": 2400000}, {"name": "123.0 MHz", "center_freq": 123000000, "sample_rate": 2400000}, {"name": "121.0 MHz", "center_freq": 121000000, "sample_rate": 2400000}, {"name": "119.0 MHz", "center_freq": 119000000, "sample_rate": 2400000}, {"name": "1090MHz ADSB", "center_freq": 1090000000, "sample_rate": 2400000}, {"name": "DAB 6A", "center_freq": 181936000, "sample_rate": 2048000}, {"name": "DAB 7A", "center_freq": 188928000, "sample_rate": 2048000}, {"name": "DAB 7D", "center_freq": 194064000, "sample_rate": 2048000}, {"name": "DAB 9A", "center_freq": 202928000, "sample_rate": 2048000}, {"name": "DAB 9C", "center_freq": 206352000, "sample_rate": 2048000}, {"name": "DAB 9D", "center_freq": 208064000, "sample_rate": 2048000}, {"name": "DAB 11B", "center_freq": 218640000, "sample_rate": 2048000}, {"name": "DAB 11C", "center_freq": 220352000, "sample_rate": 2048000}, {"name": "DAB 12B", "center_freq": 225648000, "sample_rate": 2048000}, {"name": "DAB 12C", "center_freq": 227360000, "sample_rate": 2048000}]}]}


# https://owrx2.fustinoni.net/clients ma con autenticazione


def devices_staus_change_listener(devices: dict[str, str], device_profile: dict[str, str]) -> None:
    global latest_message
    latest_message = {name: status if status == "Stopped" else device_profile[name] if name in device_profile.keys() else "Running" for name, status in devices.items()}
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
        devices_staus_change_listener(*devices_status.get_devices_status())
        uvicorn.run(app, host="0.0.0.0", port=8000)
