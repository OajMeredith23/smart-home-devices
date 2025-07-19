# Pico MQTT Controller

This project is a MicroPython-based controller for the Raspberry Pi Pico (or similar microcontroller) that connects to Wi-Fi and communicates with an MQTT broker. It allows remote control of a relay and an LED (with PWM brightness control) via MQTT messages, and provides heartbeat/status updates.

## Features
- **Wi-Fi Connectivity:** Connects to a Wi-Fi network using credentials in `secrets.py`.
- **MQTT Communication:** Subscribes to topics for relay control, LED brightness, and ping requests.
- **Relay Control:** Remotely turn a relay on or off via MQTT.
- **LED Brightness:** Set the brightness of an LED using PWM via MQTT.
- **Heartbeat:** Publishes a heartbeat/status message to indicate the device is online.
- **Automatic Reconnect:** Handles Wi-Fi and MQTT reconnections automatically.

## File Overview
- `index.py`: Main entry point. Sets up hardware, defines MQTT topics, and handles incoming MQTT messages.
- `mqtt_client.py`: Contains the `MQTTManager` class for Wi-Fi and MQTT management, including reconnection and heartbeat logic.
- `secrets.py`: Stores Wi-Fi and MQTT broker credentials, and the device name.

## MQTT Topics
Assuming `DEVICE_NAME = "pico"` (as in `secrets.py`):

- `pico/relay` — Control the relay:
    - Payload: `on` or `off`
- `pico/led/brightness` — Set LED brightness:
    - Payload: Integer `0`–`100` (percent)
- `pico/ping` — Ping the device:
    - Any payload; device will print a message when received

## Example MQTT Requests

Ensure your MQTT client is running on the IP address matching the 'MQTT_SERVER' in secrets.py

### Turn Relay On
```
topic: pico/relay
payload: on
```

### Turn Relay Off
```
topic: pico/relay
payload: off
```

e.g. `mosquitto_pub -h localhost -t pico/relay -m "off"`

### Set LED Brightness to 75% (example of using a range, not implemented with any hardware)
```
topic: pico/led/brightness
payload: 75
```


### Ping the Device
```
topic: pico/ping
payload: (any value)
```

e.g. `mosquitto_pub -h localhost -t pico/ping -m "hello"`

## Usage
1. Flash the code to your Pico running MicroPython.
2. Update `secrets.py` with your Wi-Fi and MQTT broker details.
3. Power on the device. It will connect to Wi-Fi and the MQTT broker, then subscribe to the topics above.
4. Use any MQTT client (e.g., [MQTT Explorer](https://mqtt-explorer.com/), `mosquitto_pub`, Home Assistant, etc.) to publish messages to the topics.

---

**Note:**
- The onboard LED flashes during Wi-Fi and MQTT connection attempts.
- The device will automatically reconnect if Wi-Fi or MQTT connection is lost.
- Heartbeat/status is published every 30 seconds.
