# main.py

from machine import Pin, PWM
import time
from mqtt_client import MQTTManager
from secrets import DEVICE_NAME

# Setup hardware
relay = Pin(18, Pin.OUT)
led_pwm = PWM(Pin(15))
led_pwm.freq(1000)

# MQTT Topics
TOPICS = [
    f"{DEVICE_NAME}/relay".encode(),
    f"{DEVICE_NAME}/led/brightness".encode(),
    f"{DEVICE_NAME}/ping".encode()
]

# MQTT message handler
def handle_mqtt(topic, msg):
    print(f"Topic: {topic}, Message: {msg}")

    if topic == b'pico/relay':
        if msg == b'on':
            relay.value(1)
        elif msg == b'off':
            relay.value(0)

    elif topic == b'pico/led/brightness':
        try:
            val = int(msg)
            val = min(max(val, 0), 100)
            duty = int((val / 100) * 65535)
            # led_pwm.duty_u16(duty)
            print(f"Setting LED brightness to {val}% (duty cycle: {duty})")
        except ValueError:
            print("Invalid brightness value")

    elif topic == b'pico/ping':
        print("Ping received — I’m alive!")

def main():
    mqtt = MQTTManager("pico_modular_client", TOPICS, handle_mqtt)
    mqtt.connect_wifi()
    mqtt.setup_mqtt()

    try:
        while True:
            mqtt.loop()
            time.sleep(0.1)
    finally:
        mqtt.disconnect()

main()
