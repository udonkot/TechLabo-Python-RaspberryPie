#!/usr/bin/env python3
"""
Wiiリモコン制御クラス
"""

import threading
import evdev
from evdev import InputDevice, categorize, ecodes

from config.config import Config
from config.device_detector import DeviceDetector
from config.robot_component import RobotComponent


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
    
    def __init__(self, pi, robot_controller):
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

        # キーコードをボタン名に変換
        button_name = None
        keycode = key_event.keycode
        print(keycode)  # デバッグ用
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
            'left': lambda: self.robot.scroll_help(-1),      # Modified: LCD help scroll down
            'right': lambda: self.robot.scroll_help(1),     # Modified: LCD help scroll up
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
