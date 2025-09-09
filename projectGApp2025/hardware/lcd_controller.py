#!/usr/bin/env python3
"""
LCD制御クラス
"""

import pigpio
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

from ..config import RobotComponent


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
