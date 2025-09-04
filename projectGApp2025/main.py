#!/usr/bin/env python3
"""
Gundam-style Robot Controller for Raspberry Pi 4
Wiiリモコン操作によるLED、カメラ、サーボモーター制御システム
"""

import os
import time
import random
import threading
import queue
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path

# 必要なライブラリのインポート
import RPi.GPIO as GPIO
import pygame
from picamera2 import Picamera2
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import cwiid
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

# ===== 設定クラス =====
class Config:
    """設定を管理するクラス"""
    
    # GPIO ピン設定
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
    
    # Slack設定（環境変数から読み込み）
    SLACK_TOKEN = os.environ.get('SLACK_BOT_TOKEN', 'your-slack-token-here')
    SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#general')
    
    # カメラ設定
    CAMERA_RESOLUTION = (1920, 1080)
    CAMERA_PREVIEW_TIME = 3  # カウントダウン秒数
    
    # サウンド設定
    SOUNDS_DIR = Path('./sounds')
    
    @classmethod
    def load_from_file(cls, filepath: str = 'config.json'):
        """JSONファイルから設定を読み込む"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config = json.load(f)
                for key, value in config.items():
                    setattr(cls, key, value)

# ===== 基底クラス =====
class RobotComponent:
    """ロボットコンポーネントの基底クラス"""
    
    def __init__(self, name: str):
        self.name = name
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

# ===== LED制御クラス =====
class LEDController(RobotComponent):
    """LED制御を管理するクラス"""
    
    def __init__(self):
        super().__init__("LED Controller")
        self.pins = Config.PINS['leds']
        self.setup_pins()
        self.patterns = self._load_patterns()
        
    def setup_pins(self):
        """GPIO ピンの初期設定"""
        for name, pin in self.pins.items():
            if isinstance(pin, list):
                for p in pin:
                    GPIO.setup(p, GPIO.OUT)
                    GPIO.output(p, GPIO.LOW)
            else:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
    
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
                    GPIO.output(p, GPIO.HIGH if state else GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
    
    def _pattern_startup(self):
        """起動時のLEDパターン"""
        all_leds = []
        for pin in self.pins.values():
            if isinstance(pin, list):
                all_leds.extend(pin)
            else:
                all_leds.append(pin)
        
        for led in all_leds:
            GPIO.output(led, GPIO.HIGH)
            time.sleep(0.05)
        time.sleep(0.5)
        for led in all_leds:
            GPIO.output(led, GPIO.LOW)
            time.sleep(0.05)
    
    def _pattern_vulcan(self):
        """バルカン砲発射パターン"""
        vulcan_pin = self.pins['face_vulcan']
        for _ in range(20):
            GPIO.output(vulcan_pin, GPIO.HIGH)
            time.sleep(0.05)
            GPIO.output(vulcan_pin, GPIO.LOW)
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
            GPIO.output(led, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(led, GPIO.LOW)
    
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
                GPIO.output(led, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(led, GPIO.LOW)
    
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
                GPIO.output(led, GPIO.HIGH)
            time.sleep(0.2)
            for led in all_leds:
                GPIO.output(led, GPIO.LOW)
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
                    GPIO.output(led, GPIO.HIGH)
                time.sleep(0.15)
                for led in group:
                    GPIO.output(led, GPIO.LOW)
    
    def _pattern_konami(self):
        """コナミコマンド成功時の特別パターン"""
        # 全LED高速点滅
        all_leds = []
        for pin in self.pins.values():
            if isinstance(pin, list):
                all_leds.extend(pin)
            else:
                all_leds.append(pin)
        
        for _ in range(10):
            for led in all_leds:
                GPIO.output(led, GPIO.HIGH)
            time.sleep(0.05)
            for led in all_leds:
                GPIO.output(led, GPIO.LOW)
            time.sleep(0.05)
        
        # スパイラルパターン
        self._pattern_wave()
        
    def play_pattern(self, pattern_name: str):
        """指定されたパターンを実行"""
        if pattern_name in self.patterns:
            thread = threading.Thread(target=self.patterns[pattern_name])
            thread.daemon = True
            thread.start()
    
    def cleanup(self):
        """全LEDをオフにしてクリーンアップ"""
        for pin in self.pins.values():
            if isinstance(pin, list):
                for p in pin:
                    GPIO.output(p, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.LOW)

# ===== サーボモーター制御クラス =====
class ServoController(RobotComponent):
    """サーボモーター制御クラス"""
    
    def __init__(self):
        super().__init__("Servo Controller")
        self.pin = Config.PINS['servo']
        self.pwm = None
        self.current_angle = 90
        self.setup()
        
    def setup(self):
        """サーボモーターの初期設定"""
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 50)  # 50Hz
        self.pwm.start(0)
        self.move_to_angle(90)  # 中央位置
        
    def move_to_angle(self, angle: int):
        """指定角度に移動"""
        if 0 <= angle <= 180:
            duty_cycle = 2.5 + (angle / 180.0) * 10.0
            self.pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.5)
            self.pwm.ChangeDutyCycle(0)  # 停止
            self.current_angle = angle
    
    def rotate_step(self, step: int = 10):
        """ステップ単位で回転"""
        new_angle = self.current_angle + step
        new_angle = max(0, min(180, new_angle))
        self.move_to_angle(new_angle)
    
    def sweep(self):
        """スイープ動作"""
        for angle in range(0, 180, 10):
            self.move_to_angle(angle)
            time.sleep(0.1)
        for angle in range(180, 0, -10):
            self.move_to_angle(angle)
            time.sleep(0.1)
        self.move_to_angle(90)
    
    def cleanup(self):
        """サーボモーターのクリーンアップ"""
        if self.pwm:
            self.pwm.stop()

# ===== カメラ制御クラス =====
class CameraController(RobotComponent):
    """カメラ制御クラス"""
    
    def __init__(self, lcd_controller=None):
        super().__init__("Camera Controller")
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
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = Path(f"./captures/{filename}")
        filepath.parent.mkdir(exist_ok=True)
        
        # カウントダウン
        for i in range(Config.CAMERA_PREVIEW_TIME, 0, -1):
            if self.lcd:
                self.lcd.display_text(f"撮影まで: {i}", "Smile!")
            time.sleep(1)
        
        if self.lcd:
            self.lcd.display_text("撮影中!", "チーズ!")
        
        # 撮影
        self.camera.capture_file(str(filepath))
        
        if self.lcd:
            self.lcd.display_text("撮影完了!", str(filename))
        
        return str(filepath)
    
    def cleanup(self):
        """カメラのクリーンアップ"""
        if self.camera:
            self.camera.stop()

# ===== LCD制御クラス =====
class LCDController(RobotComponent):
    """LCD制御クラス"""
    
    def __init__(self):
        super().__init__("LCD Controller")
        self.device = None
        self.setup()
        
    def setup(self):
        """LCDの初期設定"""
        try:
            serial = i2c(port=1, address=0x3C)
            self.device = ssd1306(serial, width=128, height=64)
            self.display_text("System Ready", "待機中...")
        except Exception as e:
            print(f"LCD初期化エラー: {e}")
            self.device = None
    
    def display_text(self, line1: str, line2: str = ""):
        """テキストを表示"""
        if not self.device:
            return
            
        with canvas(self.device) as draw:
            draw.text((0, 0), line1, fill="white")
            if line2:
                draw.text((0, 20), line2, fill="white")
    
    def display_pattern(self, pattern: str):
        """パターン表示"""
        patterns = {
            'startup': "起動中...",
            'ready': "準備完了!",
            'vulcan': "バルカン発射!",
            'konami': "隠しコマンド発動!"
        }
        text = patterns.get(pattern, "")
        if text:
            self.display_text(text)
    
    def cleanup(self):
        """LCDのクリーンアップ"""
        if self.device:
            self.device.clear()

# ===== Slack連携クラス =====
class SlackUploader(RobotComponent):
    """Slack連携クラス"""
    
    def __init__(self):
        super().__init__("Slack Uploader")
        self.client = WebClient(token=Config.SLACK_TOKEN)
        
    def upload_image(self, filepath: str, message: str = "新しい写真を撮影しました！"):
        """画像をSlackにアップロード"""
        try:
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
    
    def __init__(self):
        super().__init__("Sound Controller")
        pygame.mixer.init()
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        """サウンドファイルを読み込む"""
        sound_files = {
            'vulcan': 'vulcan.wav',
            'startup': 'startup.wav',
            'capture': 'shutter.wav',
            'alert': 'alert.wav',
            'konami': 'secret.wav',
            'bgm': 'bgm.mp3'
        }
        
        Config.SOUNDS_DIR.mkdir(exist_ok=True)
        for name, filename in sound_files.items():
            filepath = Config.SOUNDS_DIR / filename
            if filepath.exists():
                self.sounds[name] = pygame.mixer.Sound(str(filepath))
    
    def play_sound(self, sound_name: str):
        """指定された音を再生"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_bgm(self, filename: str = 'bgm.mp3'):
        """BGMを再生"""
        filepath = Config.SOUNDS_DIR / filename
        if filepath.exists():
            pygame.mixer.music.load(str(filepath))
            pygame.mixer.music.play(-1)  # ループ再生
    
    def stop_bgm(self):
        """BGMを停止"""
        pygame.mixer.music.stop()
    
    def cleanup(self):
        """音響システムのクリーンアップ"""
        pygame.mixer.quit()

# ===== 赤外線センサークラス =====
class IRSensorController(RobotComponent):
    """赤外線センサー制御クラス"""
    
    def __init__(self, callback=None):
        super().__init__("IR Sensor")
        self.pin = Config.PINS['ir_sensor']
        self.callback = callback
        self.setup()
        self._monitoring = False
        self._monitor_thread = None
        
    def setup(self):
        """赤外線センサーの初期設定"""
        GPIO.setup(self.pin, GPIO.IN)
        
    def start_monitoring(self):
        """監視を開始"""
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        
    def _monitor_loop(self):
        """監視ループ"""
        last_state = GPIO.input(self.pin)
        while self._monitoring:
            current_state = GPIO.input(self.pin)
            if current_state != last_state and current_state == GPIO.HIGH:
                if self.callback:
                    self.callback()
            last_state = current_state
            time.sleep(0.1)
    
    def stop_monitoring(self):
        """監視を停止"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
    
    def cleanup(self):
        """クリーンアップ"""
        self.stop_monitoring()

# ===== Wiiリモコンコントローラー =====
class WiiRemoteController(RobotComponent):
    """Wiiリモコン制御クラス"""
    
    def __init__(self, robot_controller):
        super().__init__("Wii Remote")
        self.robot = robot_controller
        self.wii = None
        self.konami_sequence = []
        self.konami_code = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right', '2', '1']
        self.button_combo = {}
        self.connect()
        
    def connect(self):
        """Wiiリモコンに接続"""
        print("Wiiリモコンを探しています... (1+2ボタンを押してください)")
        try:
            self.wii = cwiid.Wiimote()
            self.wii.rpt_mode = cwiid.RPT_BTN
            self.wii.led = 1  # LED1を点灯
            print("Wiiリモコン接続成功!")
            return True
        except RuntimeError:
            print("Wiiリモコンが見つかりません")
            return False
    
    def check_konami_code(self, button: str):
        """コナミコマンドのチェック"""
        self.konami_sequence.append(button)
        if len(self.konami_sequence) > len(self.konami_code):
            self.konami_sequence.pop(0)
        
        if self.konami_sequence == self.konami_code:
            self.konami_sequence = []
            return True
        return False
    
    def handle_button(self, buttons: int):
        """ボタン入力を処理"""
        # 横持ち用のボタンマッピング
        button_map = {
            cwiid.BTN_LEFT: 'left',     # 十字キー左
            cwiid.BTN_RIGHT: 'right',   # 十字キー右  
            cwiid.BTN_UP: 'up',         # 十字キー上
            cwiid.BTN_DOWN: 'down',     # 十字キー下
            cwiid.BTN_2: '2',           # 2ボタン
            cwiid.BTN_1: '1',           # 1ボタン
            cwiid.BTN_A: 'a',           # Aボタン
            cwiid.BTN_B: 'b',           # Bボタン（トリガー）
            cwiid.BTN_PLUS: 'plus',     # +ボタン
            cwiid.BTN_MINUS: 'minus',   # -ボタン
            cwiid.BTN_HOME: 'home'      # HOMEボタン
        }
        
        # Bボタンが押されているか確認
        b_pressed = bool(buttons & cwiid.BTN_B)
        
        for btn_code, btn_name in button_map.items():
            if buttons & btn_code:
                # コナミコマンドチェック
                if self.check_konami_code(btn_name):
                    self.robot.execute_konami_command()
                    continue
                
                # Bボタンとの組み合わせ
                if b_pressed and btn_name != 'b':
                    self.robot.execute_combo_command(btn_name)
                    continue
                
                # 通常のボタン処理
                self.process_button_action(btn_name)
    
    def process_button_action(self, button: str):
        """ボタンアクションを実行"""
        actions = {
            'left': lambda: self.robot.servo.rotate_step(-10),
            'right': lambda: self.robot.servo.rotate_step(10),
            'up': lambda: self.robot.servo.rotate_step(10),
            'down': lambda: self.robot.servo.rotate_step(-10),
            '2': lambda: self.robot.fire_vulcan(),
            '1': lambda: self.robot.random_light_show(),
            'a': lambda: self.robot.capture_photo(),
            'plus': lambda: self.robot.lcd.display_text("Mode:", "Battle"),
            'minus': lambda: self.robot.lcd.display_text("Mode:", "Standby"),
            'home': lambda: self.robot.show_status()
        }
        
        action = actions.get(button)
        if action:
            action()
    
    def start_listening(self):
        """ボタン入力の監視を開始"""
        if not self.wii:
            return
            
        thread = threading.Thread(target=self._listen_loop)
        thread.daemon = True
        thread.start()
    
    def _listen_loop(self):
        """監視ループ"""
        last_buttons = 0
        while self.wii:
            try:
                buttons = self.wii.state['buttons']
                if buttons != last_buttons:
                    self.handle_button(buttons)
                last_buttons = buttons
                time.sleep(0.05)
            except Exception as e:
                print(f"Wiiリモコンエラー: {e}")
                break
    
    def cleanup(self):
        """クリーンアップ"""
        if self.wii:
            self.wii.close()

# ===== メインロボットコントローラー =====
class GundamRobotController:
    """メインのロボット制御システム"""
    
    def __init__(self):
        # GPIO初期化
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # コンポーネント初期化
        self.led = LEDController()
        self.servo = ServoController()
        self.lcd = LCDController()
        self.camera = CameraController(self.lcd)
        self.slack = SlackUploader()
        self.sound = SoundController()
        self.ir_sensor = IRSensorController(callback=self.on_motion_detected)
        self.wii_remote = None
        
        # 状態管理
        self.is_running = True
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
        time.sleep(2)
        self.lcd.display_pattern('ready')
        print("起動完了！")
        
    def connect_wii_remote(self):
        """Wiiリモコンを接続"""
        self.wii_remote = WiiRemoteController(self)
        if self.wii_remote.wii:
            self.wii_remote.start_listening()
            return True
        return False
    
    def fire_vulcan(self):
        """バルカン発射"""
        self.lcd.display_pattern('vulcan')
        self.led.play_pattern('vulcan')
        self.sound.play_sound('vulcan')
        
    def random_light_show(self):
        """ランダムライトショー"""
        self.lcd.display_text("Light Show!", "Random Mode")
        self.led.play_pattern('random')
        
    def capture_photo(self):
        """写真撮影とSlackアップロード"""
        filepath = self.camera.capture_with_countdown()
        if filepath:
            self.sound.play_sound('capture')
            # Slack アップロードを非同期で実行
            thread = threading.Thread(
                target=lambda: self.slack.upload_image(
                    filepath, 
                    f"ガンダムロボットからの写真 📸 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            )
            thread.daemon = True
            thread.start()
    
    def on_motion_detected(self):
        """モーション検知時の処理"""
        print("動きを検知！")
        self.lcd.display_text("Motion!", "Detected!")
        self.led.play_pattern('alert')
        self.sound.play_sound('alert')
        # 自動撮影
        self.capture_photo()
        
    def execute_konami_command(self):
        """コナミコマンド実行"""
        print("隠しコマンド発動！")
        self.lcd.display_pattern('konami')
        self.led.play_pattern('konami')
        self.sound.play_sound('konami')
        self.servo.sweep()
        self.sound.play_bgm()
        
    def execute_combo_command(self, button: str):
        """Bボタンコンボコマンド"""
        combos = {
            'up': 'wave',
            'down': 'rainbow',
            'left': 'alert',
            'right': 'startup'
        }
        
        pattern = combos.get(button)
        if pattern:
            self.lcd.display_text("Combo!", f"B + {button.upper()}")
            self.led.play_pattern(pattern)
            
    def show_status(self):
        """ステータス表示"""
        status = f"Servo: {self.servo.current_angle}°"
        self.lcd.display_text("Status", status)
        
    def start_ir_monitoring(self):
        """赤外線センサー監視開始"""
        self.ir_sensor.start_monitoring()
        
    def run(self):
        """メインループ"""
        try:
            # Wiiリモコン接続
            if not self.connect_wii_remote():
                print("Wiiリモコンなしで起動します")
            
            # 赤外線センサー監視開始
            self.start_ir_monitoring()
            
            print("\nシステム稼働中... (Ctrl+Cで終了)")
            print("=" * 50)
            print("Wiiリモコン操作方法（横持ち）:")
            print("十字キー: サーボモーター制御")
            print("②ボタン: バルカン発射")
            print("①ボタン: ランダムライトショー") 
            print("Aボタン: カメラ撮影")
            print("Bボタン + 他: コンボ技")
            print("隠しコマンド: ↑↑↓↓←→←→②①")
            print("=" * 50)
            
            # メインループ
            while self.is_running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n終了処理中...")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """全体のクリーンアップ"""
        self.is_running = False
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
                component.cleanup()
                
        GPIO.cleanup()
        print("システム終了")

# ===== エントリーポイント =====
if __name__ == "__main__":
    # 設定ファイルがあれば読み込み
    Config.load_from_file()
    
    # ロボットコントローラー起動
    robot = GundamRobotController()
    robot.run()