#!/usr/bin/env python3
"""
設定管理クラス
"""

import os
import json


class Config:
    """設定を管理するクラス"""
    
    # GPIO ピン設定 (BCM番号)
    PINS = {
        'servo': 18,
        'leds': {
            'face_head': 16,
            'face_eyes': 21,
            'face_vulcan': 20,
            'shoulder_right_up': 6,
            'shoulder_left_up': 19,
            'shoulder_right_down': 13,
            'shoulder_left_down': 26,
            'chest': [25, 24],
            'back': 5,
            'foot_left': [23, 17],
            'foot_right': [27, 22]
        },
        'ir_sensor': 4
    }
    
    # Wiiリモコンデバイスパス
    WIIMOTE_DEVICE_PATH = "/dev/input/event8"  # 環境に応じて変更
    
    # Slack設定（環境変数から読み込み）
    SLACK_TOKEN = os.environ.get('SLACK_BOT_TOKEN', 'your-slack-token-here')
    SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#general')
    
    # カメラ設定
    CAMERA_RESOLUTION = (1920, 1080)
    CAMERA_PREVIEW_TIME = 3  # カウントダウン秒数
    
    # サウンド設定
    SOUNDS_DIR = './sounds'
    
    # サーボモーター設定
    SERVO_MIN_PULSE = 500   # 最小パルス幅 (μs)
    SERVO_MAX_PULSE = 2500  # 最大パルス幅 (μs)
    
    @classmethod
    def load_from_file(cls, filepath: str = 'config.json'):
        """JSONファイルから設定を読み込む"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config = json.load(f)
                for key, value in config.items():
                    setattr(cls, key, value)
