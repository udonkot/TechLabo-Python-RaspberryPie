import pygame
import numpy as np

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

def create_beep(frequency, duration, filename):
    sample_rate = 22050
    frames = int(duration * sample_rate)
    arr = np.array([4096 * np.sin(2.0 * np.pi * frequency * x / sample_rate) 
                     for x in range(frames)]).astype(np.int16)
    stereo = np.array([arr, arr]).T
    stereo = np.ascontiguousarray(stereo)  # C-contiguousに変換
    sound = pygame.sndarray.make_sound(stereo)
    pygame.mixer.Sound.set_volume(sound, 0.5)
    # WAVファイルとして保存
    import wave
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo.tobytes())

# サンプルサウンド生成
create_beep(440, 0.5, 'sounds/alert.wav')
create_beep(880, 0.2, 'sounds/vulcan.wav')