import asyncio
import os
import sys
import time
import pygame
import RPi.GPIO as GPIO

# Add the root directory of your project to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append('/home/rpiuser/github_repo/TechLabo-Python-RaspberryPie/projectGApp/accounts/utils')

from projectGApp.accounts.utils import ledUtils

# Initialize pygame for music playback
pygame.mixer.init()

# Setup GPIO pins (example uses GPIO.BOARD mode for pin numbering)
LED_PIN = 20
LIGHT_GROUP_ALL = [20,21,6,13,19,26,16,25]

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

async def play_music(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(1)  # Wait for 1 second and check if music is still playing

async def blink_led(pin, interval=1):
    time.sleep(5),

    for i in range(1,5):
        GPIO.output(pin, GPIO.HIGH)  # Turn LED on
        await asyncio.sleep(interval)  # Wait for 'interval' seconds
        GPIO.output(pin, GPIO.LOW)  # Turn LED off
        await asyncio.sleep(interval)  # Wait for 'interval' seconds
        

async def main():
    # Run both tasks concurrently
    await asyncio.gather(
        play_music('/home/rpiuser/opt/sounds/kensirou.mp3'),
        time.sleep(5),
        ledUtils.randomLighting(LIGHT_GROUP_ALL, 0.5, 5),
        time.sleep(5),
        ledUtils.lightsOn(LIGHT_GROUP_ALL),
    )

# Run the main function in the asyncio event loop
if __name__ == '__main__':
    asyncio.run(main())