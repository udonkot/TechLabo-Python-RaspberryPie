#!/usr/bin/env python3
"""
LCD制御クラス
"""

import pigpio
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

from config.robot_component import RobotComponent


class LCDController(RobotComponent):
    """LCD制御クラス"""
    
    def __init__(self, pi, address=0x27):
        """
        LCDの初期化
        :param pi: pigpioインスタンス
        :param address: LCDのI2Cアドレス
        """
        super().__init__("LCD Controller", pi)
        self.address = address
        self.device = None
        self.setup()

    def setup(self):
        """LCDの初期設定"""
        try:
            serial = i2c(port=1, address=0x27)
            self.device = ssd1306(serial, width=128, height=64)
            self.display_text("System Ready", "Standby...")
        except Exception as e:
            print(f"LCD initialization error: {e}")
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
            'startup': ("Starting up...", ""),
            'ready': ("Ready!", "Operational"),
            'vulcan': ("Vulcan Fire!", "Rapid shots"),
            'konami': ("Secret Command!", "Activated!"),
            'motion': ("Motion detected!", "Auto capture")
        }
        text = patterns.get(pattern, ("", ""))
        self.display_text(text[0], text[1])
    
    def cleanup(self):
        """LCDのクリーンアップ"""
        if self.device:
            self.device.clear()
