#!/usr/bin/env python3
"""
LED制御クラス
"""

import time
import random
import threading
from typing import Dict

import pigpio

from config.config import Config
from config.robot_component import RobotComponent


class LEDController(RobotComponent):
    """LED制御を管理するクラス"""
    
    def __init__(self, pi: pigpio.pi):
        super().__init__("LED Controller", pi)
        self.pins = Config.PINS['leds']
        self.setup_pins()
        self.patterns = self._load_patterns()
        self._pattern_threads = []
        
    def setup_pins(self):
        """GPIO ピンの初期設定"""
        for name, pin in self.pins.items():
            if isinstance(pin, list):
                for p in pin:
                    self.pi.set_mode(p, pigpio.OUTPUT)
                    self.pi.write(p, 0)
            else:
                self.pi.set_mode(pin, pigpio.OUTPUT)
                self.pi.write(pin, 0)
    
    def _load_patterns(self) -> Dict:
        """LED点灯パターンを読み込む"""
        return {
            'startup': self._pattern_startup,
            'vulcan': self._pattern_vulcan,
            'random': self._pattern_random,
            'wave': self._pattern_wave,
            'alert': self._pattern_alert,
            'rainbow': self._pattern_rainbow,
            'konami': self._pattern_konami
        }
    
    def set_led(self, name: str, state: bool):
        """特定のLEDをオン/オフ"""
        if name in self.pins:
            pin = self.pins[name]
            if isinstance(pin, list):
                for p in pin:
                    self.pi.write(p, 1 if state else 0)
            else:
                self.pi.write(pin, 1 if state else 0)
    
    def set_led_pwm(self, name: str, brightness: int):
        """PWMでLEDの明るさを制御 (0-255)"""
        if name in self.pins:
            pin = self.pins[name]
            if isinstance(pin, list):
                for p in pin:
                    self.pi.set_PWM_dutycycle(p, brightness)
            else:
                self.pi.set_PWM_dutycycle(pin, brightness)
    
    def _pattern_startup(self):
        """起動時のLEDパターン"""
        all_leds = []
        for pin in self.pins.values():
            if isinstance(pin, list):
                all_leds.extend(pin)
            else:
                all_leds.append(pin)
        
        # フェードイン効果
        for brightness in range(0, 256, 5):
            for led in all_leds:
                self.pi.set_PWM_dutycycle(led, brightness)
            time.sleep(0.01)
        
        time.sleep(0.5)
        
        # フェードアウト効果
        for brightness in range(255, -1, -5):
            for led in all_leds:
                self.pi.set_PWM_dutycycle(led, brightness)
            time.sleep(0.01)
    
    def _pattern_vulcan(self):
        """バルカン砲発射パターン"""
        vulcan_pin = self.pins['face_vulcan']
        for _ in range(20):
            self.pi.write(vulcan_pin, 1)
            time.sleep(0.05)
            self.pi.write(vulcan_pin, 0)
            time.sleep(0.05)
    
    def _pattern_random(self):
        """ランダム点灯パターン"""
        all_leds = []
        for pin in self.pins.values():
            if isinstance(pin, list):
                all_leds.extend(pin)
            else:
                all_leds.append(pin)
        
        for _ in range(30):
            led = random.choice(all_leds)
            self.pi.write(led, 1)
            time.sleep(0.1)
            self.pi.write(led, 0)
    
    def _pattern_wave(self):
        """ウェーブパターン"""
        sequence = [
            self.pins['face_head'],
            self.pins['face_eyes'],
            self.pins['shoulder_right_up'],
            self.pins['shoulder_left_up'],
            self.pins['chest'][0],
            self.pins['back'],
            self.pins['foot_left'][0],
            self.pins['foot_right'][0]
        ]
        
        for _ in range(3):
            for led in sequence:
                self.pi.write(led, 1)
                time.sleep(0.1)
                self.pi.write(led, 0)
    
    def _pattern_alert(self):
        """警告パターン"""
        all_leds = []
        for pin in self.pins.values():
            if isinstance(pin, list):
                all_leds.extend(pin)
            else:
                all_leds.append(pin)
        
        for _ in range(5):
            for led in all_leds:
                self.pi.write(led, 1)
            time.sleep(0.2)
            for led in all_leds:
                self.pi.write(led, 0)
            time.sleep(0.2)
    
    def _pattern_rainbow(self):
        """レインボーパターン"""
        groups = [
            [self.pins['face_head'], self.pins['face_eyes']],
            [self.pins['shoulder_right_up'], self.pins['shoulder_left_up']],
            self.pins['chest'],
            [self.pins['back']],
            self.pins['foot_left'],
            self.pins['foot_right']
        ]
        
        for _ in range(3):
            for group in groups:
                for led in group:
                    self.pi.write(led, 1)
                time.sleep(0.15)
                for led in group:
                    self.pi.write(led, 0)
    
    def _pattern_konami(self):
        """コナミコマンド成功時の特別パターン"""
        all_leds = []
        for pin in self.pins.values():
            if isinstance(pin, list):
                all_leds.extend(pin)
            else:
                all_leds.append(pin)
        
        # 高速フラッシュ
        for _ in range(10):
            for led in all_leds:
                self.pi.write(led, 1)
            time.sleep(0.05)
            for led in all_leds:
                self.pi.write(led, 0)
            time.sleep(0.05)
        
        # 回転パターン
        self._pattern_wave()
    
    def play_pattern(self, pattern_name: str):
        """指定されたパターンを実行"""
        if pattern_name in self.patterns:
            thread = threading.Thread(target=self.patterns[pattern_name])
            thread.daemon = True
            thread.start()
            self._pattern_threads.append(thread)
    
    def cleanup(self):
        """全LEDをオフにしてクリーンアップ"""
        for pin in self.pins.values():
            if isinstance(pin, list):
                for p in pin:
                    self.pi.set_PWM_dutycycle(p, 0)
                    self.pi.write(p, 0)
            else:
                self.pi.set_PWM_dutycycle(pin, 0)
                self.pi.write(pin, 0)
