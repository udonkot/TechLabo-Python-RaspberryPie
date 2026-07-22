#!/usr/bin/env python3
"""
デバイス検出ヘルパークラス
"""

from typing import Optional
import evdev
from evdev import InputDevice


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
