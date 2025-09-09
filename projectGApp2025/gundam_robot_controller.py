#!/usr/bin/env python3
"""
メインロボット制御クラス
"""

import time
import threading
import queue
from datetime import datetime

import pigpio

from config.config import Config
from hardware.lcd_controller import LCDController
from hardware.led_controller import LEDController
from hardware.servo_controller import ServoController
from hardware.sound_controller import SoundController
from hardware.camera_controller import CameraController
from hardware.ir_sensor_controller import IRSensorController

from communication.slack_uploader import SlackUploader
from communication.wii_remote_controller import WiiRemoteController
from lcd1602Test import LCD1602Test


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
        time.sleep(2)
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
