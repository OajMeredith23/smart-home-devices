# mqtt_client.py

import network
import time
from umqtt.simple import MQTTClient
from secrets import WIFI_SSID, WIFI_PASSWORD, MQTT_SERVER
from machine import Pin

# Onboard LED (used for status indication like flashing during reconnects)
ONBOARD_LED = Pin("LED", Pin.OUT)

# Heartbeat configuration
_HEARTBEAT_TOPIC = b"pico/status"
_HEARTBEAT_INTERVAL = 30  # seconds
_last_heartbeat = 0  # time of the last heartbeat sent


class MQTTManager:
    def __init__(self, client_id, topics, message_callback):
        """
        Initialize the MQTTManager.
        - client_id: Unique MQTT client ID for the device
        - topics: List of MQTT topics to subscribe to
        - message_callback: Function to call when a message is received
        """
        self.topics = topics
        self.message_callback = message_callback
        self.client_id = client_id
        self.client = None  # MQTTClient instance will be set in setup_mqtt()
        self.wlan = network.WLAN(network.STA_IF)  # Wi-Fi station mode

    def _flash_led(self, flashes=1, duration=0.2):
        """
        Flash the onboard LED a number of times.
        Used for visual feedback during connection attempts.
        """
        for _ in range(flashes):
            ONBOARD_LED.on()
            time.sleep(duration)
            ONBOARD_LED.off()
            time.sleep(duration)

    def connect_wifi(self):
        """
        Connect to Wi-Fi using credentials from secrets.py.
        Flashes LED while trying to connect.
        """
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print("Connecting to Wi-Fi...")
            self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            while not self.wlan.isconnected():
                self._flash_led()
        print("Wi-Fi connected:", self.wlan.ifconfig())

    def setup_mqtt(self):
        global _last_heartbeat

        if self.client:
            try:
                self.client.disconnect()
            except:
                pass

        # Create MQTT client WITHOUT will arguments
        self.client = MQTTClient(self.client_id, MQTT_SERVER, keepalive=60)

        # Set Last Will manually (required in MicroPython)
        self.client.set_last_will(
            topic=_HEARTBEAT_TOPIC,
            msg=b"offline",
            retain=True,
            qos=0
        )

        self.client.set_callback(self.message_callback)

        print("Connecting to MQTT broker...")
        connected = False
        while not connected:
            try:
                self.client.connect()
                connected = True
            except OSError as e:
                print("MQTT connect failed, retrying...")
                self._flash_led(flashes=2)
                time.sleep(2)

        for topic in self.topics:
            self.client.subscribe(topic)
            print(f"Subscribed to: {topic}")

        self.publish_heartbeat()
        _last_heartbeat = time.time()

    def publish_heartbeat(self):
        """
        Publish a heartbeat message to indicate the device is online.
        Uses a retained message so new subscribers see it immediately.
        """
        if self.client:
            try:
                self.client.publish(_HEARTBEAT_TOPIC, b"online", retain=True)
            except Exception as e:
                print("Failed to publish heartbeat:", e)
        else:
            print("MQTT client not initialized, skipping heartbeat.")

    def check_messages(self):
        """
        Check for new MQTT messages.
        If connection is lost, attempt to reconnect.
        """
        if self.client:
            try:
                self.client.check_msg()
            except OSError:
                print("MQTT connection lost, reconnecting...")
                self.setup_mqtt()

    def ensure_wifi(self):
        """
        Reconnect Wi-Fi if connection is lost.
        """
        if not self.wlan.isconnected():
            print("Wi-Fi dropped, reconnecting...")
            self.connect_wifi()

    def loop(self):
        """
        Call this repeatedly in the main loop.
        It ensures Wi-Fi and MQTT connections stay active,
        handles incoming messages, and sends heartbeat messages.
        """
        global _last_heartbeat

        self.ensure_wifi()
        self.check_messages()

        # Send heartbeat every _HEARTBEAT_INTERVAL seconds
        now = time.time()
        if now - _last_heartbeat > _HEARTBEAT_INTERVAL:
            self.publish_heartbeat()
            _last_heartbeat = now

    def disconnect(self):
        """
        Gracefully disconnect from the MQTT broker.
        """
        if self.client:
            self.client.disconnect()
