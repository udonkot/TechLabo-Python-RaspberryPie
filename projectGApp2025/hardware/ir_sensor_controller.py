#!/usr/bin/env python3
"""
赤外線センサー制御クラス
"""

import time
import pigpio

from config.config import Config
from config.robot_component import RobotComponent


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
