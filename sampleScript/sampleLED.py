import time

import RPi.GPIO as GPIO

# Pin configuration
LED_PIN = 13  # Replace with the GPIO pin number you connected the LED to

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    print("LED is ON")
    GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on the LED
    time.sleep(5)  # Keep the LED on for 5 seconds
    print("LED is OFF")
    GPIO.output(LED_PIN, GPIO.LOW)  # Turn off the LED
finally:
    GPIO.cleanup()  # Clean up GPIO settings