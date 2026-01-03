# OWRX+ Devices Status Plugin

Devices status reporter plugin for [OpenWebRX+](https://github.com/luarvique/openwebrx).

## Overview
This software implement a "Receiver Plugin" base on the [OpenWebRX+ plugin architecture](https://github.com/0xAF/openwebrxplus-plugins).
This plugin extends the status panel by displaying the profile name each receiver is currently tuned to, or "Stopped" if inactive. This is particularly useful in multi-user environments, allowing users to identify free devices.

The plugin consists of two main components:
- **Server**: A Python-based backend using FastAPI to handle HTTP requests and Server-Sent Events (SSE) for real-time updates.
- **Client**: A JavaScript frontend that dynamically updates the OpenWebRX+ status panel.


## Prerequisites

- OpenWebRX+ installation connected to an MQTT broker.
- An MQTT broker (e.g., Mosquitto) accessible by both OpenWebRX+ and this plugin.

---

## Configuration

The server requires the following environment variables:

```env
MQTT_BROKER_URL=           # MQTT broker URL
MQTT_BROKER_PORT=          # MQTT broker port
MQTT_USERNAME=             # MQTT username (optional)
MQTT_PASSWORD=             # MQTT password (optional)
MQTT_USE_TLS=true          # Use TLS for MQTT (true/false)
OWRX_RECEIVER_URL=http://localhost:8073/status.json  # OpenWebRX+ receiver status URL
MQTT_TOPIC_DEVICE_STATUS=openwebrx/RX  # MQTT topic for device status
MQTT_CLIENT_ID=            # MQTT client ID
```

Set these variables according to your installation.

---

## Installation

### Install the Plugin in OpenWebRX+

To install the plugin in OpenWebRX+, edit the `init.js` file under the `plugins/receiver` directory (location may vary). Add the following lines:

```javascript
Plugins.owrx_devices_status_API_URL = 'http://<server_url>'; // Optional
Plugins.load('http://<server_url>/devices-static/owrx_devices_status.js');
```

Replace `<server_url>` with the URL of the server running this plugin.

---

### Running the Application Directly

1. **Install Dependencies**  
   Create a virtual environment and install the required dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**  
   Set the necessary environment variables as described in the Configuration section.

3. **Run the Server**  
   Start the server with the following command:

   ```bash
   python device_status_server.py
   ```

4. **Access the Web Interface**  
   Open a web browser and navigate to:

   ```
   http://localhost:8000/devices-static/index.html
   ```

   To fully render the page, copy the following files from your OpenWebRX+ installation to the `devices-static` directory:
   - `openwebrx.css`
   - `openwebrx-globals.css`
   - `openwebrx-header.css`

---

### Running the Application with Docker

1. **Configure Environment Variables**  
   Edit the `docker-compose.yml` file to set the necessary environment variables.

2. **Run the Docker Compose File**  
   Start the application using:

   ```bash
   docker-compose up -d
   ```

---

## Notes

- The server logs errors if it fails to retrieve device profiles, and defaults to an empty JSON object.

