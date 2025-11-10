#!/usr/bin/env python3
import RPi.GPIO as GPIO
import os
import time

PIN = 27  # physical pin 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Ready to detect shutdown button press... (hold 2s to shutdown)")

try:
    while True:
        GPIO.wait_for_edge(PIN, GPIO.FALLING)
        press_time = time.time()
        while GPIO.input(PIN) == GPIO.LOW:
            if time.time() - press_time >= 2:
                print("Button held for 2s, shutting down...")
                os.system("sudo shutdown -h now")
                break
            time.sleep(0.1)
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
