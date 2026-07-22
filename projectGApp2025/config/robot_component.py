#!/usr/bin/env python3
"""
ロボットコンポーネント基底クラス
"""

import pigpio


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
