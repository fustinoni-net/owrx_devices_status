import logging
from typing import Callable

import paho.mqtt.client as mqtt
import requests

from pydantic_settings import BaseSettings
from pydantic import BaseModel


logging.basicConfig(level=logging.INFO)

class Settings(BaseSettings):
    mqtt_broker_url: str  = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_use_tls: bool = False
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_topic_device_status: str = "openwebrx/RX"
    mqtt_client_id: str = "OwrxDevicesStatus"
    # receiver url
    owrx_receiver_url: str = "http://localhost:8073/status.json"


settings = Settings()
logging.info(f"mqtt broker url: {settings.mqtt_broker_url}")
logging.info(f"mqtt broker pot: {settings.mqtt_broker_port}")
logging.info(f"mqtt use tls: {settings.mqtt_use_tls}")
logging.info(f"mqtt client id: {settings.mqtt_client_id}")
logging.info(f"mqtt topic for devices staus: {settings.mqtt_topic_device_status}")
logging.info(f"OWRX URL of the status.json resource:  {settings.owrx_receiver_url}")

def get_devices_profiles(url: str) -> tuple[list[str], str]:
    logging.info(f"get_devices_profiles: Fetching SDR profiles from {url}")

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        st = resp.json()
    except Exception as exc:
        logging.error("get_devices_profiles: error getting profile from %s: %s", url, exc)
        st ={}

    logging.info(f"get_devices_profiles: Json used to get profiles: {st}")
    sdr_names: list[str] = list(map(lambda sdr: sdr["name"], filter(lambda sdr: "name" in sdr, st["sdrs"])))
    start_profile_name: str = st["sdrs"][0]["profiles"][0]["name"]

    return sdr_names, start_profile_name

class OwrxDevicesStatus:
    def __init__(self, config_setting: Settings):
        super().__init__()
        self.devices: dict[str, str] = {}
        self.device_profile: dict[str, str] = {}

        self.owrx_receiver_url = config_setting.owrx_receiver_url

        self.set_devices_from_receiver()

        self.broker_url = config_setting.mqtt_broker_url
        self.broker_port = config_setting.mqtt_broker_port
        self.username = config_setting.mqtt_username
        self.password = config_setting.mqtt_password
        self.mqtt_use_tls = config_setting.mqtt_use_tls
        self.mqtt_client = mqtt.Client(client_id=config_setting.mqtt_client_id, protocol=mqtt.MQTTv311)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.topic_device_state = config_setting.mqtt_topic_device_status

        self.devices_status_change_listeners: list[Callable[[dict[str, str]], None]] = []
        self._notify_devices_status_change(self.prepare_massage_to_send())


    def set_devices_from_receiver(self):
        sdr_names: list[str]
        start_profile_name: str
        sdr_names, start_profile_name = get_devices_profiles(self.owrx_receiver_url)
        self.devices: dict[str, str] = {name: "Stopped" for name in sdr_names}
        self.device_profile: dict[str, str] = {list(self.devices.keys())[0]: start_profile_name}

    def __enter__(self):
        if self.username:
            self.mqtt_client.username_pw_set(self.username, self.password)

        if self.mqtt_use_tls:
            self.mqtt_client.tls_set()

        self.mqtt_client.connect(self.broker_url, self.broker_port, 60)
        self.mqtt_client.loop_start()
        logging.info(f"OwrxDevicesStatus: Connected to MQTT broker at {self.broker_url}:{self.broker_port}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        logging.info(f"OwrxDevicesStatus: Disconnected from MQTT broker")

    def _on_connect(self, client, userdata, flags, rc):
        logging.info(f"OwrxDevicesStatus: Connected to MQTT broker with result code {rc}")
        client.subscribe(self.topic_device_state)

    def _on_message(self, client, userdata, msg):
        latest_message = msg.payload.decode()
        logging.info(f"OwrxDevicesStatus: Received message: {latest_message}")

        class RXMessage(BaseModel):
            mode: str
            timestamp: int
            source_id: str | None = None
            source: str | None = None
            profile_id: str | None = None
            profile: str | None = None
            freq: int | None = None
            samplerate: int | None = None
            state: str | None = None

        payload = RXMessage.model_validate_json(latest_message)

        logging.info(f"OwrxDevicesStatus: payload source: {payload.source}")

        if payload.state:
            logging.info(f"OwrxDevicesStatus: payload state: {payload.state}")
            if payload.state == "ServerStarted":
                self.set_devices_from_receiver()
            else:
                if payload.source in self.devices.keys():
                    self.devices.update({payload.source: payload.state})
        else:
            logging.info(f"OwrxDevicesStatus: payload profile: {payload.profile}")
            if payload.profile:
                if payload.source in self.devices.keys():
                    self.device_profile.update({payload.source: payload.profile})


        logging.info(self.devices)
        logging.info(self.device_profile)
        # Broadcast the message to all connected clients
        self._notify_devices_status_change(self.prepare_massage_to_send())



    def prepare_massage_to_send(self) -> dict[str, str]:
        latest_message: dict[str, str] = {name: status if status == "Stopped" else self.device_profile[name] if name in self.device_profile.keys() else "Running" for name, status in self.devices.items()}
        return latest_message


    def set_devices_status_change_listener(self, devices_status_has_changed: Callable[[dict[str, str]], None]) -> None:
        self.devices_status_change_listeners.append(devices_status_has_changed)


    def _notify_devices_status_change(self, message: dict[str, str]):
        for listener in self.devices_status_change_listeners:
            listener(message)



owrx_devices_status = OwrxDevicesStatus(settings)
