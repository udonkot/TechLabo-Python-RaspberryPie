import asyncio
import time
import pygame
import RPi.GPIO as GPIO

# Initialize pygame for music playback
pygame.mixer.init()

# Setup GPIO pins (example uses GPIO.BOARD mode for pin numbering)
LED_PIN = 20
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
        play_music('/home/rpiuser/opt/sounds/gundam_voice_amuro1.mp3'),
        blink_led(LED_PIN, 0.5)  # Blink every 0.5 seconds
    )

# Run the main function in the asyncio event loop
if __name__ == '__main__':
    asyncio.run(main())