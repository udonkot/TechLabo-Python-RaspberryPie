#!/usr/bin/env python3
"""
カメラ制御クラス
"""

import time
from datetime import datetime
from typing import Optional
from pathlib import Path

import pigpio
from picamera2 import Picamera2

from config.config import Config
from config.robot_component import RobotComponent


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
