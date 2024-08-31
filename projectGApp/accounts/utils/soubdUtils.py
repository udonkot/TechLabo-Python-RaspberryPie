import asyncio
import pygame

# Initialize pygame for music playback
pygame.mixer.init()

# 非同期で音楽再生
async def play_music(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(1)  # Wait for 1 second and check if music is still playing
