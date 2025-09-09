#!/usr/bin/env python3
"""
Gundam Robot Controller メインエントリーポイント
"""

import time
import subprocess

from config import Config
from gundam_robot_controller import GundamRobotController


def main():
    """メイン関数"""
    # pigpiodデーモンが起動しているか確認
    try:
        result = subprocess.run(['pgrep', 'pigpiod'], capture_output=True, text=True)
        if not result.stdout:
            print("pigpiodデーモンが起動していません。起動します...")
            subprocess.run(['sudo', 'pigpiod'])
            time.sleep(1)
    except:
        pass
    
    # 設定ファイルがあれば読み込み
    Config.load_from_file()
    
    # ロボットコントローラー起動
    try:
        robot = GundamRobotController()
        robot.run()
    except Exception as e:
        print(f"起動エラー: {e}")
        print("\n以下を確認してください:")
        print("1. sudo pigpiod が実行されているか")
        print("2. 必要なライブラリがインストールされているか")
        print("3. GPIO配線が正しいか")


if __name__ == "__main__":
    main()
