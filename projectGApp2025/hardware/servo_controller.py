#!/usr/bin/env python3
"""
サーボモーター制御クラス
"""

import time
import pigpio

from config.config import Config
from config.robot_component import RobotComponent


class ServoController(RobotComponent):
    """サーボモーター制御クラス"""
    
    def __init__(self, pi: pigpio.pi):
        super().__init__("Servo Controller", pi)
        self.pin = Config.PINS['servo']
        self.current_angle = 90
        self.setup()
        
    def setup(self):
        """サーボモーターの初期設定"""
        self.move_to_angle(90)  # 中央位置
        
    def move_to_angle(self, angle: int):
        """指定角度に移動"""
        if 0 <= angle <= 180:
            pulse_width = Config.SERVO_MIN_PULSE + (angle / 180.0) * (Config.SERVO_MAX_PULSE - Config.SERVO_MIN_PULSE)
            self.pi.set_servo_pulsewidth(self.pin, pulse_width)
            self.current_angle = angle
            time.sleep(0.3)  # 移動待ち
    
    def rotate_step(self, step: int = 10):
        """ステップ単位で回転"""
        new_angle = self.current_angle + step
        new_angle = max(0, min(180, new_angle))
        self.move_to_angle(new_angle)
        return new_angle
    
    def smooth_move(self, target_angle: int, speed: float = 0.02):
        """滑らかに目標角度まで移動"""
        if not (0 <= target_angle <= 180):
            return
            
        current = self.current_angle
        step = 1 if target_angle > current else -1
        
        for angle in range(current, target_angle + step, step):
            self.move_to_angle(angle)
            time.sleep(speed)
    
    def sweep(self):
        """スイープ動作"""
        for angle in range(0, 181, 5):
            self.move_to_angle(angle)
            time.sleep(0.02)
        for angle in range(180, -1, -5):
            self.move_to_angle(angle)
            time.sleep(0.02)
        self.move_to_angle(90)
    
    def cleanup(self):
        """サーボモーターのクリーンアップ"""
        self.pi.set_servo_pulsewidth(self.pin, 0)  # パルス停止
