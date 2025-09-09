"""
Gundam Robot Controller Package - フォルダ構成版

ガンダム風ロボットコントローラーのメインパッケージ
機能別フォルダに整理された構成
"""

# 設定・共通モジュール
from .config import Config, DeviceDetector, RobotComponent

# ハードウェア制御モジュール
from .hardware import (
    LEDController, ServoController, CameraController,
    LCDController, SoundController, IRSensorController
)

# 通信・連携モジュール
from .communication import SlackUploader, WiiRemoteController

# メインシステム
from .gundam_robot_controller import GundamRobotController
from .main_final import main

__version__ = "4.0.0"
__author__ = "Robot Team"
__description__ = "機能別フォルダ構成のガンダムロボットコントローラー"

__all__ = [
    # 設定・共通
    'Config',
    'DeviceDetector', 
    'RobotComponent',
    # ハードウェア制御
    'LEDController',
    'ServoController',
    'CameraController',
    'LCDController',
    'SoundController', 
    'IRSensorController',
    # 通信・連携
    'SlackUploader',
    'WiiRemoteController',
    # メインシステム
    'GundamRobotController',
    'main'
]

# モジュール分類情報
PACKAGE_STRUCTURE = {
    'config': [
        'Config',
        'DeviceDetector',
        'RobotComponent'
    ],
    'hardware': [
        'LEDController',
        'ServoController', 
        'CameraController',
        'LCDController',
        'SoundController',
        'IRSensorController'
    ],
    'communication': [
        'SlackUploader',
        'WiiRemoteController'
    ],
    'main': [
        'GundamRobotController',
        'main'
    ]
}

def get_package_info():
    """パッケージ構成情報を取得"""
    return {
        'version': __version__,
        'structure': PACKAGE_STRUCTURE,
        'total_modules': sum(len(modules) for modules in PACKAGE_STRUCTURE.values())
    }
