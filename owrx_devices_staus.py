import logging
from typing import Callable

import paho.mqtt.client as mqtt

from pydantic_settings import BaseSettings
from pydantic import BaseModel


logging.basicConfig(level=logging.INFO)

class Settings(BaseSettings):
    mqtt_broker_url: str  = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None

    # MQTT topics
    # mqtt_topic_device_state: str = "openwebrx/hp-owrx/RX"
    mqtt_topic_device_state: str = "openwebrx/raspi-owrx/RX"

    # receiver url
    owrx_receiver_url: str = "http://localhost:8073"


settings = Settings()
logging.info(settings.mqtt_broker_url)
logging.info(settings.mqtt_broker_port)
logging.info(settings.mqtt_topic_device_state)

def get_devices_profiles(url: str) -> tuple[list[str], str]:

    logging.info(f"get_devices_profiles: Fetching SDR profiles from {url}")
    st = {"receiver": {
        "name": "<font color='black'  style='background-color: rgba(255, 255, 255, 0.5);'>  IK2ZSH </font>",
        "admin": "example@example.com", "gps": {"lat": 45.7007212405664, "lon": 9.65270348173823}, "asl": 300,
        "location": "<font color='black'  style='background-color: rgba(255, 255, 255, 0.5);'>  Bergamo, Bg, Italy  </font>"},
          "max_clients": 5, "version": "v1.2.103", "sdrs": [{"name": "RTL-SDR v4", "type": "RtlSdrSource", "profiles": [
            {"name": "439.200 MHz", "center_freq": 439200000, "sample_rate": 2400000},
            {"name": "437.200 MHz", "center_freq": 437200000, "sample_rate": 2400000},
            {"name": "435.200 MHz", "center_freq": 435200000, "sample_rate": 2400000},
            {"name": "433.200 MHz", "center_freq": 433200000, "sample_rate": 2400000},
            {"name": "431.200 MHz - 70cm Repeaters", "center_freq": 431200000, "sample_rate": 2400000},
            {"name": "145 MHz 2m", "center_freq": 145000000, "sample_rate": 2400000},
            {"name": "29.5 MHz", "center_freq": 29500000, "sample_rate": 2400000},
            {"name": "29.5 MHz vert 11m 1/4\u03bb", "center_freq": 29500000, "sample_rate": 2400000},
            {"name": "27.5 MHz", "center_freq": 27500000, "sample_rate": 2400000},
            {"name": "27.5 MHz  vert 11m 1/4\u03bb", "center_freq": 27500000, "sample_rate": 2400000},
            {"name": "25.5 MHz", "center_freq": 25500000, "sample_rate": 2400000},
            {"name": "25.5 MHz  vert 11m 1/4\u03bb", "center_freq": 25500000, "sample_rate": 2400000},
            {"name": "23.5 MHz", "center_freq": 23500000, "sample_rate": 2400000},
            {"name": "21.5 MHz", "center_freq": 21500000, "sample_rate": 2400000},
            {"name": "19.5 MHz", "center_freq": 19500000, "sample_rate": 2400000},
            {"name": "17.5 MHz", "center_freq": 17500000, "sample_rate": 2400000},
            {"name": "15.5 MHz", "center_freq": 15500000, "sample_rate": 2400000},
            {"name": "13.5 MHz", "center_freq": 13500000, "sample_rate": 2400000},
            {"name": "11.5 MHz", "center_freq": 11500000, "sample_rate": 2400000},
            {"name": "9.5 MHz", "center_freq": 9500000, "sample_rate": 2400000},
            {"name": "7.5 MHz", "center_freq": 7500000, "sample_rate": 2400000},
            {"name": "5.5 MHz", "center_freq": 5500000, "sample_rate": 2400000},
            {"name": "3.5 MHz", "center_freq": 3500000, "sample_rate": 2400000},
            {"name": "1.5 MHz", "center_freq": 1500000, "sample_rate": 2400000},
            {"name": "137.0 MHz", "center_freq": 137000000, "sample_rate": 2400000},
            {"name": "135.0 MHz", "center_freq": 135000000, "sample_rate": 2400000},
            {"name": "133.0 MHz", "center_freq": 133000000, "sample_rate": 2400000},
            {"name": "131.0 MHz", "center_freq": 131000000, "sample_rate": 2400000},
            {"name": "129.0 MHz", "center_freq": 129000000, "sample_rate": 2400000},
            {"name": "127.0 MHz", "center_freq": 127000000, "sample_rate": 2400000},
            {"name": "125.0 MHz", "center_freq": 125000000, "sample_rate": 2400000},
            {"name": "123.0 MHz", "center_freq": 123000000, "sample_rate": 2400000},
            {"name": "121.0 MHz", "center_freq": 121000000, "sample_rate": 2400000},
            {"name": "119.0 MHz", "center_freq": 119000000, "sample_rate": 2400000},
            {"name": "1090MHz ADSB", "center_freq": 1090000000, "sample_rate": 2400000},
            {"name": "ISM 433", "center_freq": 433900000, "sample_rate": 2400000},
            {"name": "PMR", "center_freq": 446000000, "sample_rate": 2400000},
            {"name": "PMR 433,600", "center_freq": 433600000, "sample_rate": 2600000},
            {"name": "40.680 MHz - 8m", "center_freq": 40680000, "sample_rate": 1800000}]},
                                                            {"name": "SDRPlay", "type": "SdrplaySource", "profiles": [
                                                                {"name": "10m", "center_freq": 28850000,
                                                                 "sample_rate": 2000000},
                                                                {"name": "11m CB", "center_freq": 27000000,
                                                                 "sample_rate": 2000000},
                                                                {"name": "12m", "center_freq": 24940000,
                                                                 "sample_rate": 250000},
                                                                {"name": "15m", "center_freq": 21225000,
                                                                 "sample_rate": 500000},
                                                                {"name": "17m", "center_freq": 18118000,
                                                                 "sample_rate": 250000},
                                                                {"name": "20m", "center_freq": 14175000,
                                                                 "sample_rate": 500000},
                                                                {"name": "30m", "center_freq": 10125000,
                                                                 "sample_rate": 250000},
                                                                {"name": "40m", "center_freq": 7150000,
                                                                 "sample_rate": 500000},
                                                                {"name": "60m", "center_freq": 5350000,
                                                                 "sample_rate": 250000},
                                                                {"name": "80m", "center_freq": 3750000,
                                                                 "sample_rate": 500000},
                                                                {"name": "160m", "center_freq": 1900000,
                                                                 "sample_rate": 250000},
                                                                {"name": "AM Broadcast", "center_freq": 1100000,
                                                                 "sample_rate": 2000000},
                                                                {"name": "49m Broadcast", "center_freq": 6050000,
                                                                 "sample_rate": 500000},
                                                                {"name": "41m Broadcast", "center_freq": 7325000,
                                                                 "sample_rate": 250000},
                                                                {"name": "31m Broadcast", "center_freq": 9650000,
                                                                 "sample_rate": 500000},
                                                                {"name": "25m Broadcast", "center_freq": 11850000,
                                                                 "sample_rate": 500000},
                                                                {"name": "22m Broadcast", "center_freq": 13720000,
                                                                 "sample_rate": 500000},
                                                                {"name": "433MHz ISM", "center_freq": 433000000,
                                                                 "sample_rate": 2000000},
                                                                {"name": "1090MHz ADSB", "center_freq": 1090000000,
                                                                 "sample_rate": 4000000},
                                                                {"name": "2m", "center_freq": 145000000,
                                                                 "sample_rate": 5000000},
                                                                {"name": "30-40m", "center_freq": 8500000,
                                                                 "sample_rate": 4000000}]},
                                                            {"name": "Nooelec sdr", "type": "RtlSdrSource",
                                                             "profiles": [
                                                                 {"name": "437.200 MHz", "center_freq": 437200000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "435.200 MHz", "center_freq": 435200000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "433.200 MHz", "center_freq": 433200000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "431.200 MHz - 70cm Repeaters",
                                                                  "center_freq": 431200000, "sample_rate": 2400000},
                                                                 {"name": "145 MHz 2m", "center_freq": 145000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "53.58 MHz", "center_freq": 52800000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "51.0 MHz", "center_freq": 51000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "29.5 MHz", "center_freq": 29500000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "27.5 MHz", "center_freq": 27500000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "137.0 MHz", "center_freq": 137000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "135.0 MHz", "center_freq": 135000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "133.0 MHz", "center_freq": 133000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "131.0 MHz", "center_freq": 131000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "129.0 MHz", "center_freq": 129000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "127.0 MHz", "center_freq": 127000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "125.0 MHz", "center_freq": 125000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "123.0 MHz", "center_freq": 123000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "121.0 MHz", "center_freq": 121000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "119.0 MHz", "center_freq": 119000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "1090MHz ADSB", "center_freq": 1090000000,
                                                                  "sample_rate": 2400000},
                                                                 {"name": "DAB 6A", "center_freq": 181936000,
                                                                  "sample_rate": 2048000},
                                                                 {"name": "DAB 7A", "center_freq": 188928000,
                                                                  "sample_rate": 2048000},
                                                                 {"name": "DAB 7D", "center_freq": 194064000,
                                                                  "sample_rate": 2048000},
                                                                 {"name": "DAB 9A", "center_freq": 202928000,
                                                                  "sample_rate": 2048000},
                                                                 {"name": "DAB 9C", "center_freq": 206352000,
                                                                  "sample_rate": 2048000},
                                                                 {"name": "DAB 9D", "center_freq": 208064000,
                                                                  "sample_rate": 2048000},
                                                                 {"name": "DAB 11B", "center_freq": 218640000,
                                                                  "sample_rate": 2048000},
                                                                 {"name": "DAB 11C", "center_freq": 220352000,
                                                                  "sample_rate": 2048000},
                                                                 {"name": "DAB 12B", "center_freq": 225648000,
                                                                  "sample_rate": 2048000},
                                                                 {"name": "DAB 12C", "center_freq": 227360000,
                                                                  "sample_rate": 2048000}]}]}

    sdr_names: list[str] = list(map(lambda sdr: sdr["name"], filter(lambda sdr: "name" in sdr, st["sdrs"])))
    start_profile_name: str = st["sdrs"][0]["profiles"][0]["name"]

    return sdr_names, start_profile_name

class OwrxDevicesStatus:
    def __init__(self, settings: Settings):
        super().__init__()
        self.devices: dict[str, str] = {}
        self.device_profile: dict[str, str] = {}

        self.owrx_receiver_url = settings.owrx_receiver_url

        self.set_devices_from_receiver()

        self.broker_url = settings.mqtt_broker_url
        self.broker_port = settings.mqtt_broker_port
        self.username = settings.mqtt_username
        self.password = settings.mqtt_password
        self.mqtt_client = mqtt.Client(client_id="OwrxDevicesStatus", protocol=mqtt.MQTTv311)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.topic_device_state = settings.mqtt_topic_device_state

        self.devices_status_change_listeners: list[Callable[[dict[str, str], dict[str, str]], None]] = []
        self._notify_devices_status_change(self.devices, self.device_profile)

    def get_devices_status(self) -> tuple[dict[str, str], dict[str, str]]:
        return self.devices, self.device_profile


    def set_devices_from_receiver(self):
        sdr_names: list[str]
        start_profile_name: str
        sdr_names, start_profile_name = get_devices_profiles(self.owrx_receiver_url)
        self.devices: dict[str, str] = {name: "Stopped" for name in sdr_names}
        self.device_profile: dict[str, str] = {list(self.devices.keys())[0]: start_profile_name}

    def __enter__(self):
        self.mqtt_client.username_pw_set(self.username, self.password)

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
                self.devices.update({payload.source: payload.state})
        else:
            logging.info(f"OwrxDevicesStatus: payload profile: {payload.profile}")
            if payload.profile:
                self.device_profile.update({payload.source: payload.profile})


        logging.info(self.devices)
        logging.info(self.device_profile)
        # Broadcast the message to all connected clients
        self._notify_devices_status_change(self.devices, self.device_profile)


    def set_devices_status_change_listener(self, devices_status_has_changed: Callable[[dict[str, str], dict[str, str]], None]) -> None:
        """
        Notify about the antenna change.
        """
        self.devices_status_change_listeners.append(devices_status_has_changed)


    def _notify_devices_status_change(self, devices: dict[str, str], device_profile: dict[str, str]):
        for listener in self.devices_status_change_listeners:
            listener(devices, device_profile)



owrx_devices_status = OwrxDevicesStatus(settings)
