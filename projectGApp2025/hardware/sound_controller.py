#!/usr/bin/env python3
"""
音響制御クラス
"""

from pathlib import Path
import pygame
from playsound import playsound

from config.config import Config
from config.robot_component import RobotComponent


class SoundController(RobotComponent):
    """音響制御クラス"""
    
    def __init__(self, pi):
        super().__init__("Sound Controller", pi)
        pygame.mixer.init()
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        """サウンドファイルを読み込む"""
        sound_files = {
            'vulcan': 'vulcan.wav',
            'startup': 'monoai.mp3',
            'capture': 'shutter.wav',
            'alert': 'alert.wav',
            'konami': 'gundamBGM1.mp3',
            'bgm': 'gundam_op.mp3'
        }
        
        Path(Config.SOUNDS_DIR).mkdir(exist_ok=True)
        for name, filename in sound_files.items():
            filepath = Path(Config.SOUNDS_DIR) / filename
            if filepath.exists():
                print(filepath)
                self.sounds[name] = filepath
            else:
                print(f"サウンドファイル未検出: {filepath}")
    
    def play_sound(self, sound_name: str):
        """指定された音を再生"""
        if sound_name in self.sounds:
            print(self.sounds[sound_name])
            playsound(self.sounds[sound_name])
    
    def play_bgm(self, filename: str = 'bgm.mp3'):
        """BGMを再生"""
        filepath = Path(Config.SOUNDS_DIR) / filename
        if filepath.exists():
            playsound(filepath)
    
    def stop_bgm(self):
        """BGMを停止"""
        pygame.mixer.music.stop()
    
    def cleanup(self):
        """音響システムのクリーンアップ"""
        pygame.mixer.quit()
