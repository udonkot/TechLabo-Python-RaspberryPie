#!/usr/bin/env python3
"""
Gundam-style Robot Controller for Raspberry Pi 4
Wiiリモコン操作によるLED、カメラ、サーボモーター制御システム
evdev + pigpio 版
"""

import os
import time
import random
import threading
import queue
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json
from pathlib import Path
import subprocess

# 必要なライブラリのインポート
import evdev
from evdev import InputDevice, categorize, ecodes
import pigpio
import pygame
from picamera2 import Picamera2
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

from lcd1602Test import LCD1602Test
from playsound import playsound

# ===== 設定クラス =====
class Config:
    """設定を管理するクラス"""
    
    # GPIO ピン設定 (BCM番号)
    PINS = {
        'servo': 18,
        'leds': {
            'face_head': 21,
            'face_eyes': 20,
            'face_vulcan': 12,
            'shoulder_right_up': 26,
            'shoulder_left_up': 19,
            'shoulder_right_down': 16,
            'shoulder_left_down': 15,
            'chest': [6, 24],
            'back': 13,
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
    SOUNDS_DIR = Path('./sounds')
    
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

# ===== デバイス検出ヘルパー =====
class DeviceDetector:
    """入力デバイスを自動検出するヘルパークラス"""
    
    @staticmethod
    def find_wiimote() -> Optional[str]:
        """Wiiリモコンのデバイスパスを自動検出"""
        devices = [InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            # Wiiリモコンの名前パターンをチェック
            if 'Nintendo Wii Remote' in device.name or 'Nintendo RVL-CNT-01' in device.name:
                print(f"Wiiリモコンを検出: {device.name} at {device.path}")
                return device.path
        return None
    
    @staticmethod
    def list_all_devices():
        """接続されている全デバイスをリスト表示"""
        devices = [InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            print(f"{device.path}: {device.name}")
            capabilities = device.capabilities(verbose=True)
            print(f"  Capabilities: {list(capabilities.keys())}")

# ===== 基底クラス =====
class RobotComponent:
    """ロボットコンポーネントの基底クラス"""
    
    def __init__(self, name: str, pi: pigpio.pi = None):
        self.name = name
        self.pi = pi
        self._is_active = False
        
    def activate(self):
        """コンポーネントを有効化"""
        self._is_active = True
        
    def deactivate(self):
        """コンポーネントを無効化"""
        self._is_active = False
        
    def cleanup(self):
        """クリーンアップ処理"""
        pass

# ===== LED制御クラス (pigpio版) =====
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

# ===== サーボモーター制御クラス (pigpio版) =====
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

# ===== カメラ制御クラス =====
class CameraController(RobotComponent):
    """カメラ制御クラス"""
    
    def __init__(self, pi: pigpio.pi, lcd_controller=None):
        super().__init__("Camera Controller", pi)
        self.camera = None
        self.lcd = lcd_controller
        self.setup()
        
    def setup(self):
        """カメラの初期設定"""
        try:
            self.camera = Picamera2()
            config = self.camera.create_still_configuration(
                main={"size": Config.CAMERA_RESOLUTION}
            )
            self.camera.configure(config)
            self.camera.start()
            time.sleep(2)  # カメラの起動待ち
        except Exception as e:
            print(f"カメラ初期化エラー: {e}")
            self.camera = None
    
    def capture_with_countdown(self) -> Optional[str]:
        """カウントダウン付き撮影"""
        if not self.camera:
            print('no camera')
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = Path(f"./captures/{filename}")
        filepath.parent.mkdir(exist_ok=True)
        
        # カウントダウン
        for i in range(Config.CAMERA_PREVIEW_TIME, 0, -1):
            if self.lcd:
                self.lcd.display_text(f"Count Down...: {i}", "Smile!")
            time.sleep(1)
        
        if self.lcd:
            self.lcd.display_text("Fire!!", "Cheeese!!!")
        
        # 撮影
        self.camera.capture_file(str(filepath))
        
        if self.lcd:
            self.lcd.display_text("Compreted!!", str(filename))
        
        return str(filepath)
    
    def cleanup(self):
        """カメラのクリーンアップ"""
        if self.camera:
            self.camera.stop()

# ===== LCD制御クラス =====
class LCDController(RobotComponent):
    """LCD制御クラス"""
    
    # def __init__(self, pi: pigpio.pi):
    #     super().__init__("LCD Controller", pi)
    #     self.device = None
    #     self.setup()

    def __init__(self, pi, address=0x27):
        """
        LCDの初期化
        :param pi: pigpioインスタンス
        :param address: LCDのI2Cアドレス
        """
        self.pi = pi
        self.address = address
        self.setup()

    def setup(self):
        """LCDの初期設定"""
        try:
            serial = i2c(port=1, address=0x27)
            self.device = ssd1306(serial, width=128, height=64)
            self.display_text("System Ready", "待機中...")
        except Exception as e:
            print(f"LCD初期化エラー: {e}")
            self.device = None
    
    def display_text(self, line1: str, line2: str = "", line3: str = ""):
        """テキストを表示"""
        if not self.device:
            return
            
        with canvas(self.device) as draw:
            draw.text((0, 0), line1, fill="white")
            if line2:
                draw.text((0, 20), line2, fill="white")
            if line3:
                draw.text((0, 40), line3, fill="white")
    
    def display_pattern(self, pattern: str):
        """パターン表示"""
        patterns = {
            'startup': ("起動中...", ""),
            'ready': ("準備完了!", "操作可能"),
            'vulcan': ("バルカン発射!", "ドドドドド"),
            'konami': ("隠しコマンド!", "発動！！"),
            'motion': ("動体検知!", "自動撮影")
        }
        text = patterns.get(pattern, ("", ""))
        self.display_text(text[0], text[1])
    
    def cleanup(self):
        """LCDのクリーンアップ"""
        if self.device:
            self.device.clear()

# ===== Slack連携クラス =====
class SlackUploader(RobotComponent):
    """Slack連携クラス"""
    
    def __init__(self, pi: pigpio.pi):
        super().__init__("Slack Uploader", pi)
        self.client = WebClient(token=Config.SLACK_TOKEN)
        
    def upload_image(self, filepath: str, message: str = "新しい写真を撮影しました！"):
        """画像をSlackにアップロード"""
        try:
            print(Config.SLACK_CHANNEL)
            with open(filepath, 'rb') as file:
                response = self.client.files_upload_v2(
                    channel=Config.SLACK_CHANNEL,
                    file=file,
                    initial_comment=message,
                    filename=os.path.basename(filepath)
                )
                return response['ok']
        except SlackApiError as e:
            print(f"Slackアップロードエラー: {e.response['error']}")
            return False
        except Exception as e:
            print(f"予期しないエラー: {e}")
            return False

# ===== 音響制御クラス =====
class SoundController(RobotComponent):
    """音響制御クラス"""
    
    def __init__(self, pi: pigpio.pi):
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
        
        Config.SOUNDS_DIR.mkdir(exist_ok=True)
        for name, filename in sound_files.items():
            filepath = Config.SOUNDS_DIR / filename
            if filepath.exists():
                print(filepath)

                self.sounds[name] = filepath
                # self.sounds[name] = pygame.mixer.Sound(str(filepath))
            else:
                print(f"サウンドファイル未検出: {filepath}")
    
    def play_sound(self, sound_name: str):
        """指定された音を再生"""
        if sound_name in self.sounds:
            print(self.sounds[sound_name])
            playsound(self.sounds[sound_name])
    
    def play_bgm(self, filename: str = 'bgm.mp3'):
        """BGMを再生"""
        filepath = Config.SOUNDS_DIR / filename
        if filepath.exists():
            playsound(filepath)
            # pygame.mixer.music.load(str(filepath))
            # pygame.mixer.music.play(-1)  # ループ再生
    
    def stop_bgm(self):
        """BGMを停止"""
        pygame.mixer.music.stop()
    
    def cleanup(self):
        """音響システムのクリーンアップ"""
        pygame.mixer.quit()

# ===== 赤外線センサークラス =====
class IRSensorController(RobotComponent):
    """赤外線センサー制御クラス"""
    
    def __init__(self, pi: pigpio.pi, callback=None):
        super().__init__("IR Sensor", pi)
        self.pin = Config.PINS['ir_sensor']
        self.callback = callback
        self.setup()
        self._monitoring = False
        self._last_trigger_time = 0
        self._trigger_cooldown = 5  # 5秒のクールダウン
        
    def setup(self):
        """赤外線センサーの初期設定"""
        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin, pigpio.PUD_DOWN)
        
    def start_monitoring(self):
        """監視を開始"""
        self._monitoring = True
        # コールバック設定
        self.pi.callback(self.pin, pigpio.RISING_EDGE, self._on_motion)
        
    def _on_motion(self, gpio, level, tick):
        """モーション検知時のコールバック"""
        current_time = time.time()
        if current_time - self._last_trigger_time > self._trigger_cooldown:
            self._last_trigger_time = current_time
            if self.callback:
                self.callback()
    
    def stop_monitoring(self):
        """監視を停止"""
        self._monitoring = False
    
    def cleanup(self):
        """クリーンアップ"""
        self.stop_monitoring()

# ===== Wiiリモコンコントローラー (evdev版) =====
class WiiRemoteController(RobotComponent):
    """Wiiリモコン制御クラス (evdev版)"""
    
    # Wiiリモコンのボタンマッピング（横持ち）
    BUTTON_MAP = {
        'KEY_LEFT': 'left',       # 十字キー左
        'KEY_RIGHT': 'right',     # 十字キー右
        'KEY_UP': 'up',           # 十字キー上（実際は左）
        'KEY_DOWN': 'down',       # 十字キー下（実際は右）
        'BTN_1': '1',             # 1ボタン
        'BTN_2': '2',             # 2ボタン
        'BTN_A': 'a',             # Aボタン
        'BTN_B': 'b',             # Bボタン（トリガー）
        'KEY_PREVIOUS': 'minus',  # -ボタン
        'KEY_NEXT': 'plus',       # +ボタン
        'BTN_MODE': 'home',       # HOMEボタン
    }
    
    def __init__(self, pi: pigpio.pi, robot_controller):
        super().__init__("Wii Remote", pi)
        self.robot = robot_controller
        self.device = None
        self.device_path = None
        self.konami_sequence = []
        self.konami_code = ['right', 'right', 'left', 'left', 'up', 'down', 'up', 'down', '1', '2']
        self.b_pressed = False
        self._monitor_thread = None
        self._monitoring = False
        
    def connect(self) -> bool:
        """Wiiリモコンに接続"""
        print("Wiiリモコンを探しています...")
        
        # 自動検出を試みる
        self.device_path = DeviceDetector.find_wiimote()
        
        # 自動検出失敗時は設定から読み込み
        if not self.device_path:
            self.device_path = Config.WIIMOTE_DEVICE_PATH
            
        try:
            self.device = InputDevice(self.device_path)
            print(f"Wiiリモコンが接続されました: {self.device.name}")
            print(f"デバイスパス: {self.device_path}")
            
            # 利用可能なイベントタイプを表示
            capabilities = self.device.capabilities(verbose=True)
            print("利用可能な機能:")
            for event_type, codes in capabilities.items():
                print(f"  {event_type}: {len(codes)} codes")
            
            return True
            
        except FileNotFoundError:
            print(f"Wiiリモコンが見つかりませんでした: {self.device_path}")
            print("\n利用可能なデバイス:")
            DeviceDetector.list_all_devices()
            return False
        except Exception as e:
            print(f"接続エラー: {e}")
            return False
    
    def check_konami_code(self, button: str) -> bool:
        """コナミコマンドのチェック"""
        self.konami_sequence.append(button)
        if len(self.konami_sequence) > len(self.konami_code):
            self.konami_sequence.pop(0)
        
        if self.konami_sequence == self.konami_code:
            self.konami_sequence = []
            return True
        return False
    
    def handle_key_event(self, event):
        """キーイベントを処理"""
        key_event = categorize(event)
        
        # デバッグ出力
        # print(f"Key Event - Code: {key_event.keycode}, State: {key_event.keystate}")
        
        # キーコードをボタン名に変換
        button_name = None
        keycode = key_event.keycode
        if len(key_event.keycode) <= 3:
            keycode = key_event.keycode[0]
        
        if isinstance(key_event.keycode, list):
            for code in key_event.keycode:
                print(code)
                if code in self.BUTTON_MAP:
                    button_name = self.BUTTON_MAP[code]
                    break
        else:
            button_name = self.BUTTON_MAP.get(keycode)
        
        if not button_name:
            return
        
        # Bボタンの状態を追跡
        if button_name == 'b':
            self.b_pressed = (key_event.keystate == 1)  # 1=押下, 0=解放
        
        # ボタン押下時のみ処理（keystate: 0=release, 1=press, 2=hold）
        if key_event.keystate == 1:
            # コナミコマンドチェック
            if self.check_konami_code(button_name):
                self.robot.execute_konami_command()
                return
            
            # Bボタンとの組み合わせ
            if self.b_pressed and button_name != 'b':
                self.robot.execute_combo_command(button_name)
            else:
                # 通常のボタン処理
                self.process_button_action(button_name, key_event.keystate)
        
        # ボタン解放時の処理が必要な場合
        elif key_event.keystate == 0:
            if button_name in ['left', 'right', 'up', 'down']:
                # サーボモーターの停止など
                pass
    
    def handle_abs_event(self, event):
        """モーション/ジョイスティックイベントを処理"""
        abs_event = categorize(event)
        # Wiiリモコンのモーションセンサーデータ処理
        # 必要に応じて実装
        pass
    
    def process_button_action(self, button: str, state: int):
        """ボタンアクションを実行"""
        if state != 1:  # 押下時のみ処理
            return
            
        actions = {
            'left': lambda: self.robot.servo.rotate_step(-10),
            'right': lambda: self.robot.servo.rotate_step(10),
            'up': lambda: self.robot.servo.rotate_step(10),
            'down': lambda: self.robot.servo.rotate_step(-10),
            '2': lambda: self.robot.fire_vulcan(),
            '1': lambda: self.robot.random_light_show(),
            'a': lambda: self.robot.capture_photo(),
            'plus': lambda: self.robot.change_mode('battle'),
            'minus': lambda: self.robot.change_mode('standby'),
            'home': lambda: self.robot.show_status()
        }
        
        action = actions.get(button)
        if action:
            action()
    
    def start_monitoring(self):
        """ボタン入力の監視を開始"""
        if not self.device:
            return False
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        return True
    
    def _monitor_loop(self):
        """監視ループ"""
        print("Wiiリモコン監視開始...")
        
        try:
            for event in self.device.read_loop():
                if not self._monitoring:
                    break
                    
                if event.type == ecodes.EV_KEY:
                    self.handle_key_event(event)
                elif event.type == ecodes.EV_ABS:
                    self.handle_abs_event(event)
                    
        except Exception as e:
            print(f"Wiiリモコン監視エラー: {e}")
            self._monitoring = False
    
    def stop_monitoring(self):
        """監視を停止"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
    
    def cleanup(self):
        """クリーンアップ"""
        self.stop_monitoring()
        if self.device:
            try:
                self.device.close()
            except:
                pass

# ===== メインロボットコントローラー =====
class GundamRobotController:
    """メインのロボット制御システム"""
    
    def __init__(self):
        # pigpio初期化
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise Exception("pigpioデーモンに接続できません。sudo pigpiod を実行してください。")
        
        # コンポーネント初期化
        print("コンポーネントを初期化中...")
        self.led = LEDController(self.pi)
        self.servo = ServoController(self.pi)
        
        # LCDアドレスを設定から取得してLCD初期化
        try:
            lcd_address = int(getattr(Config, 'LCD_ADDRESS', '0x27'), 16)
            print(f"LCD初期化中 (アドレス: {hex(lcd_address)})...")
            # self.lcd = LCDController(self.pi, lcd_address)
            self.lcd = LCD1602Test(0x27)
            self.lcd.connect()
            self.lcd.init_lcd()
            
        except Exception as e:
            print(f"LCD初期化エラー: {e}")
            # LCDなしでも動作を続ける（ダミーオブジェクト作成）
            class DummyLCD:
                def display_text(self, *args): pass
                def display_pattern(self, *args): pass
                def set_backlight(self, *args): pass
                def clear(self): pass
                def cleanup(self): pass
            self.lcd = DummyLCD()
            print("LCD無しで続行します")
        
        self.camera = CameraController(self.pi, self.lcd)
        self.slack = SlackUploader(self.pi)
        self.sound = SoundController(self.pi)
        self.ir_sensor = IRSensorController(self.pi, callback=self.on_motion_detected)
        self.wii_remote = None
        
        # 状態管理
        self.is_running = True
        self.mode = 'standby'
        self.command_queue = queue.Queue()
        
        # 初期化完了
        self.startup_sequence()
        
    def startup_sequence(self):
        """起動シーケンス"""
        print("ガンダムロボット起動中...")
        self.lcd.display_pattern('startup')
        self.led.play_pattern('startup')
        self.sound.play_sound('startup')
        self.servo.move_to_angle(90)
        # time.sleep(2)
        self.lcd.display_pattern('ready')
        print("起動完了！")
        
    def connect_wii_remote(self) -> bool:
        """Wiiリモコンを接続"""
        self.wii_remote = WiiRemoteController(self.pi, self)
        if self.wii_remote.connect():
            return self.wii_remote.start_monitoring()
        return False
    
    def fire_vulcan(self):
        """バルカン発射"""
        print("バルカン発射！")
        self.lcd.display_pattern('vulcan')
        self.led.play_pattern('vulcan')
        self.sound.play_sound('vulcan')
        
    def random_light_show(self):
        """ランダムライトショー"""
        print("ランダムライトショー開始")
        self.lcd.display_text("Light Show!", "Random Mode")
        self.led.play_pattern('random')
        
    def capture_photo(self):
        """写真撮影とSlackアップロード"""
        print("写真撮影開始")
        filepath = self.camera.capture_with_countdown()
        if filepath:
            self.sound.play_sound('capture')
            print(f"写真保存: {filepath}")
            
            # Slack アップロードを非同期で実行
            thread = threading.Thread(
                target=self._upload_to_slack,
                args=(filepath,)
            )
            thread.daemon = True
            thread.start()
    
    def _upload_to_slack(self, filepath: str):
        """Slackへのアップロード（非同期）"""
        message = f"🤖 ガンダムロボットからの写真 📸\n撮影時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if self.slack.upload_image(filepath, message):
            print("Slackアップロード成功")
            self.lcd.display_text("Upload OK", "Slack送信完了")
        else:
            print("Slackアップロード失敗")
            self.lcd.display_text("Upload Failed", "送信失敗")
    
    def on_motion_detected(self):
        """モーション検知時の処理"""
        print("動きを検知！")
        self.lcd.display_pattern('motion')
        self.led.play_pattern('alert')
        self.sound.play_sound('alert')
        
        # 自動撮影（バトルモードの場合のみ）
        if self.mode == 'battle':
            time.sleep(1)  # 少し待機
            self.capture_photo()
        
    def execute_konami_command(self):
        """コナミコマンド実行"""
        print("🎮 隠しコマンド発動！")
        self.lcd.display_pattern('konami')
        self.led.play_pattern('konami')
        self.sound.play_sound('konami')
        
        # サーボモーターのダンス
        thread = threading.Thread(target=self.servo.sweep)
        thread.daemon = True
        thread.start()
        
        # BGM開始
        self.sound.play_bgm()
        
    def execute_combo_command(self, button: str):
        """Bボタンコンボコマンド"""
        combos = {
            'up': ('wave', 'Wave Pattern'),
            'down': ('rainbow', 'Rainbow'),
            'left': ('alert', 'Alert!'),
            'right': ('startup', 'Startup')
        }
        
        if button in combos:
            pattern, display_name = combos[button]
            print(f"コンボ発動: B + {button.upper()}")
            self.lcd.display_text("Combo!", f"B + {button.upper()}", display_name)
            self.led.play_pattern(pattern)
            
    def change_mode(self, mode: str):
        """動作モード変更"""
        self.mode = mode
        mode_display = {
            'battle': ("Mode: Battle", "battle"),
            'standby': ("Mode: Standby", "wait")
        }
        
        if mode in mode_display:
            print(f"モード変更: {mode}")
            self.lcd.display_text(*mode_display[mode])
            
    def show_status(self):
        """ステータス表示"""
        status_text = [
            "Congratulations!",
            "iglobe 21st!!!"
        ]
        # status_text = [
        #     f"Servo: {self.servo.current_angle}°",
        #     f"Uptime: {int(time.time())}s"
        # ]
        self.lcd.display_text(*status_text)
        print(f"Status - {', '.join(status_text)}")
        
    def start_ir_monitoring(self):
        """赤外線センサー監視開始"""
        print("赤外線センサー監視開始")
        self.ir_sensor.start_monitoring()
        
    def run(self):
        """メインループ"""
        try:
            # Wiiリモコン接続
            if not self.connect_wii_remote():
                print("\n⚠️  Wiiリモコンが接続できませんでした")
                print("以下のコマンドで手動接続を試してください:")
                print("  1. sudo bluetoothctl")
                print("  2. scan on")
                print("  3. Wiiリモコンの1+2ボタンを同時押し")
                print("  4. pair <MACアドレス>")
                print("  5. connect <MACアドレス>")
                print("\nWiiリモコンなしで起動を続けます...")
            
            # 赤外線センサー監視開始
            self.start_ir_monitoring()
            
            print("\n" + "="*60)
            print("🤖 ガンダムロボットシステム稼働中")
            print("="*60)
            print("\n📱 Wiiリモコン操作方法（横持ち）:")
            print("  十字キー    : サーボモーター制御")
            print("  ②ボタン    : バルカン発射")
            print("  ①ボタン    : ランダムライトショー")
            print("  Aボタン     : カメラ撮影 → Slack送信")
            print("  +ボタン     : バトルモード")
            print("  -ボタン     : スタンバイモード")
            print("  HOMEボタン  : ステータス表示")
            print("  Bボタン+他  : コンボ技")
            print("\n🎮 隠しコマンド: ↑↑↓↓←→←→②①")
            print("\n終了: Ctrl+C")
            print("="*60 + "\n")
            
            # メインループ
            while self.is_running:
                time.sleep(0.1)
                
                # コマンドキューの処理（必要に応じて）
                try:
                    while not self.command_queue.empty():
                        command = self.command_queue.get_nowait()
                        # コマンド処理
                except queue.Empty:
                    pass
                
        except KeyboardInterrupt:
            print("\n\n終了処理中...")
        except Exception as e:
            print(f"\nエラー発生: {e}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """全体のクリーンアップ"""
        self.is_running = False
        print("クリーンアップ中...")
        
        # BGM停止
        self.sound.stop_bgm()
        
        # 各コンポーネントのクリーンアップ
        components = [
            self.led, self.servo, self.lcd, 
            self.camera, self.sound, self.ir_sensor
        ]
        if self.wii_remote:
            components.append(self.wii_remote)
            
        for component in components:
            if component:
                try:
                    component.cleanup()
                except Exception as e:
                    print(f"{component.name} クリーンアップエラー: {e}")
        
        # pigpio接続を閉じる
        if self.pi.connected:
            self.pi.stop()
        
        print("✅ システム正常終了")

# ===== エントリーポイント =====
def main():
    """メイン関数"""
    # pigpiodデーモンが起動しているか確認
    try:
        result = subprocess.run(['pgrep', 'pigpiod'], capture_output=True, text=True)
        if not result.stdout:
            print("pigpiodデーモンが起動していません。起動します...")
            subprocess.run(['sudo', 'pigpiod'])
            time.sleep(1)
    except:
        pass
    
    # 設定ファイルがあれば読み込み
    Config.load_from_file()
    
    # ロボットコントローラー起動
    try:
        robot = GundamRobotController()
        robot.run()
    except Exception as e:
        print(f"起動エラー: {e}")
        print("\n以下を確認してください:")
        print("1. sudo pigpiod が実行されているか")
        print("2. 必要なライブラリがインストールされているか")
        print("3. GPIO配線が正しいか")

if __name__ == "__main__":
    main()