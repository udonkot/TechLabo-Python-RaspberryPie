#!/usr/bin/env python3
"""
LED制御クラス
"""

import time
import random
import threading
import json
import math
from typing import Dict, List, Any
from pathlib import Path

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
        self.json_patterns = self._load_json_patterns()
        self._pattern_threads = []
        self._stop_pattern = False
        
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
        """LED点灯パターンを読み込む（既存のハードコードパターン）"""
        return {
            'startup': self._pattern_startup,
            'vulcan': self._pattern_vulcan,
            'random': self._pattern_random,
            'wave': self._pattern_wave,
            'alert': self._pattern_alert,
            'rainbow': self._pattern_rainbow,
            'konami': self._pattern_konami
        }
    
    def _load_json_patterns(self) -> Dict:
        """JSONファイルからパターンを読み込む"""
        patterns = {}
        pattern_files = [
            'konami_pattern.json',
            './config/konami_pattern.json',
            './konami_pattern.json'
        ]
        
        for pattern_file in pattern_files:
            try:
                if Path(pattern_file).exists():
                    with open(pattern_file, 'r', encoding='utf-8') as f:
                        patterns.update(json.load(f))
                    print(f"JSONパターンファイル読み込み成功: {pattern_file}")
                    break
            except Exception as e:
                print(f"JSONパターンファイル読み込みエラー {pattern_file}: {e}")
        
        return patterns
    
    def get_led_pins(self, led_name: str) -> List[int]:
        """LED名からピン番号のリストを取得"""
        if led_name == "all":
            all_pins = []
            for pin in self.pins.values():
                if isinstance(pin, list):
                    all_pins.extend(pin)
                else:
                    all_pins.append(pin)
            return all_pins
        elif led_name in self.pins:
            pin = self.pins[led_name]
            return pin if isinstance(pin, list) else [pin]
        else:
            return []
    
    def set_led(self, name: str, state: bool):
        """特定のLEDをオン/オフ"""
        pins = self.get_led_pins(name)
        for pin in pins:
            self.pi.write(pin, 1 if state else 0)
    
    def set_led_pwm(self, name: str, brightness: int):
        """PWMでLEDの明るさを制御 (0-255)"""
        pins = self.get_led_pins(name)
        for pin in pins:
            self.pi.set_PWM_dutycycle(pin, brightness)
    
    def set_leds_pwm(self, led_names: List[str], brightness: int):
        """複数LEDの明るさを一括制御"""
        for name in led_names:
            self.set_led_pwm(name, brightness)
    
    def _execute_action(self, action_data: Dict[str, Any], start_time: float):
        """JSONパターンのアクションを実行"""
        action = action_data['action']
        duration = action_data.get('duration', 1.0)
        
        if action == 'fade_in_all':
            self._action_fade_in_all(duration, action_data.get('brightness', 255))
        elif action == 'fade_out_all':
            self._action_fade_out_all(duration)
        elif action == 'flash_sequence':
            self._action_flash_sequence(action_data)
        elif action == 'wave_pattern':
            self._action_wave_pattern(action_data)
        elif action == 'pulsing':
            self._action_pulsing(action_data)
        elif action == 'synchronized_flash':
            self._action_synchronized_flash(action_data)
        elif action == 'rainbow_sweep':
            self._action_rainbow_sweep(action_data)
        elif action == 'breathing':
            self._action_breathing(action_data)
        elif action == 'finale_burst':
            self._action_finale_burst(action_data)
        elif action == 'rapid_flash':
            self._action_rapid_flash(action_data)
    
    def _action_fade_in_all(self, duration: float, max_brightness: int = 255):
        """全LEDフェードイン"""
        steps = int(duration * 50)  # 50ステップ/秒
        for i in range(steps + 1):
            if self._stop_pattern:
                break
            brightness = int((i / steps) * max_brightness)
            self.set_led_pwm("all", brightness)
            time.sleep(duration / steps)
    
    def _action_fade_out_all(self, duration: float):
        """全LEDフェードアウト"""
        steps = int(duration * 50)
        for i in range(steps + 1):
            if self._stop_pattern:
                break
            brightness = int(((steps - i) / steps) * 255)
            self.set_led_pwm("all", brightness)
            time.sleep(duration / steps)
    
    def _action_flash_sequence(self, action_data: Dict[str, Any]):
        """LEDシーケンス点滅"""
        sequence = action_data.get('sequence', [])
        duration = action_data.get('duration', 2.0)
        flash_interval = action_data.get('flash_interval', 0.1)
        
        end_time = time.time() + duration
        while time.time() < end_time and not self._stop_pattern:
            for led_name in sequence:
                if self._stop_pattern or time.time() >= end_time:
                    break
                self.set_led(led_name, True)
                time.sleep(flash_interval)
                self.set_led(led_name, False)
                time.sleep(flash_interval)
    
    def _action_wave_pattern(self, action_data: Dict[str, Any]):
        """ウェーブパターン"""
        duration = action_data.get('duration', 3.0)
        wave_speed = action_data.get('wave_speed', 0.2)
        
        sequence = [
            'face_head', 'face_eyes', 'shoulder_right_up', 'shoulder_left_up',
            'chest', 'back', 'foot_left', 'foot_right'
        ]
        
        end_time = time.time() + duration
        while time.time() < end_time and not self._stop_pattern:
            for led_name in sequence:
                if self._stop_pattern or time.time() >= end_time:
                    break
                self.set_led(led_name, True)
                time.sleep(wave_speed)
                self.set_led(led_name, False)
    
    def _action_pulsing(self, action_data: Dict[str, Any]):
        """パルス点滅"""
        duration = action_data.get('duration', 4.0)
        leds = action_data.get('leds', ['chest'])
        pulse_speed = action_data.get('pulse_speed', 0.5)
        brightness_range = action_data.get('brightness_range', [50, 255])
        
        end_time = time.time() + duration
        while time.time() < end_time and not self._stop_pattern:
            # パルス上昇
            for brightness in range(brightness_range[0], brightness_range[1], 5):
                if self._stop_pattern or time.time() >= end_time:
                    break
                for led in leds:
                    self.set_led_pwm(led, brightness)
                time.sleep(pulse_speed / 40)
            
            # パルス下降
            for brightness in range(brightness_range[1], brightness_range[0], -5):
                if self._stop_pattern or time.time() >= end_time:
                    break
                for led in leds:
                    self.set_led_pwm(led, brightness)
                time.sleep(pulse_speed / 40)
    
    def _action_synchronized_flash(self, action_data: Dict[str, Any]):
        """同期フラッシュ"""
        duration = action_data.get('duration', 2.0)
        flash_pattern = action_data.get('flash_pattern', [0.1, 0.1, 0.2])
        leds = action_data.get('leds', 'all')
        
        end_time = time.time() + duration
        while time.time() < end_time and not self._stop_pattern:
            for i, interval in enumerate(flash_pattern):
                if self._stop_pattern or time.time() >= end_time:
                    break
                self.set_led(leds, i % 2 == 0)
                time.sleep(interval)
    
    def _action_rainbow_sweep(self, action_data: Dict[str, Any]):
        """レインボースイープ"""
        duration = action_data.get('duration', 5.0)
        groups = action_data.get('groups', [])
        sweep_interval = action_data.get('sweep_interval', 0.3)
        
        end_time = time.time() + duration
        while time.time() < end_time and not self._stop_pattern:
            for group in groups:
                if self._stop_pattern or time.time() >= end_time:
                    break
                for led in group:
                    self.set_led(led, True)
                time.sleep(sweep_interval)
                for led in group:
                    self.set_led(led, False)
    
    def _action_breathing(self, action_data: Dict[str, Any]):
        """呼吸パターン"""
        duration = action_data.get('duration', 6.0)
        leds = action_data.get('leds', 'all')
        breath_cycle = action_data.get('breath_cycle', 2.0)
        
        end_time = time.time() + duration
        while time.time() < end_time and not self._stop_pattern:
            # 吸い込み
            steps = int(breath_cycle * 25)
            for i in range(steps):
                if self._stop_pattern or time.time() >= end_time:
                    break
                brightness = int(127 + 127 * math.sin(i * math.pi / steps))
                self.set_led_pwm(leds, brightness)
                time.sleep(breath_cycle / steps)
    
    def _action_finale_burst(self, action_data: Dict[str, Any]):
        """フィナーレバースト"""
        duration = action_data.get('duration', 5.0)
        burst_count = action_data.get('burst_count', 10)
        burst_interval = action_data.get('burst_interval', 0.2)
        
        for _ in range(burst_count):
            if self._stop_pattern:
                break
            self.set_led("all", True)
            time.sleep(burst_interval / 2)
            self.set_led("all", False)
            time.sleep(burst_interval / 2)
    
    def _action_rapid_flash(self, action_data: Dict[str, Any]):
        """高速フラッシュ"""
        duration = action_data.get('duration', 2.0)
        leds = action_data.get('leds', ['face_vulcan'])
        flash_interval = action_data.get('flash_interval', 0.05)
        flash_count = action_data.get('flash_count', 40)
        
        for _ in range(flash_count):
            if self._stop_pattern:
                break
            for led in leds:
                self.set_led(led, True)
            time.sleep(flash_interval)
            for led in leds:
                self.set_led(led, False)
            time.sleep(flash_interval)
    
    def play_json_pattern(self, pattern_name: str):
        """JSONパターンを実行"""
        if pattern_name not in self.json_patterns:
            print(f"パターン '{pattern_name}' が見つかりません")
            return False
        
        self._stop_pattern = False
        pattern = self.json_patterns[pattern_name]
        thread = threading.Thread(target=self._execute_json_pattern, args=(pattern,))
        thread.daemon = True
        thread.start()
        self._pattern_threads.append(thread)
        return True
    
    def _execute_json_pattern(self, pattern: Dict[str, Any]):
        """JSONパターンを時間ベースで実行"""
        start_time = time.time()
        steps = sorted(pattern['steps'], key=lambda x: x['time'])
        
        for step in steps:
            if self._stop_pattern:
                break
            
            # ステップの開始時間まで待機
            step_start_time = start_time + step['time']
            wait_time = step_start_time - time.time()
            if wait_time > 0:
                time.sleep(wait_time)
            
            # アクションを別スレッドで実行
            if not self._stop_pattern:
                action_thread = threading.Thread(
                    target=self._execute_action,
                    args=(step, step_start_time)
                )
                action_thread.daemon = True
                action_thread.start()
    
    def stop_pattern(self):
        """現在実行中のパターンを停止"""
        self._stop_pattern = True
    
    # 既存のパターンメソッド（互換性のため保持）
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
        """指定されたパターンを実行（JSONパターンを優先）"""
        # まずJSONパターンを確認
        if pattern_name in self.json_patterns:
            return self.play_json_pattern(pattern_name)
        # 次に既存のハードコードパターンを確認
        elif pattern_name in self.patterns:
            thread = threading.Thread(target=self.patterns[pattern_name])
            thread.daemon = True
            thread.start()
            self._pattern_threads.append(thread)
            return True
        else:
            print(f"パターン '{pattern_name}' が見つかりません")
            return False
    
    def cleanup(self):
        """全LEDをオフにしてクリーンアップ"""
        self.stop_pattern()
        for pin in self.pins.values():
            if isinstance(pin, list):
                for p in pin:
                    self.pi.set_PWM_dutycycle(p, 0)
                    self.pi.write(p, 0)
            else:
                self.pi.set_PWM_dutycycle(pin, 0)
                self.pi.write(pin, 0)

    def all_on(self):
        """すべてのLEDを点灯"""
        for pin in self.pins.values():  # self.pins.values()を使用してピンを取得
            if isinstance(pin, list):  # ピンがリストの場合
                for p in pin:
                    self.pi.write(p, 1)  # 各ピンをHIGHに設定
            else:  # ピンが単一の整数の場合
                self.pi.write(pin, 1)  # ピンをHIGHに設定
        print("✅ All LEDs are ON")

    def all_off(self):
        """すべてのLEDを消灯"""
        for pin in self.pins.values():  # self.pins.values()を使用してピンを取得
            if isinstance(pin, list):  # ピンがリストの場合
                for p in pin:
                    self.pi.write(p, 0)  # 各ピンをLOWに設定
            else:  # ピンが単一の整数の場合
                self.pi.write(pin, 0)  # ピンをLOWに設定
        print("✅ All LEDs are OFF")
