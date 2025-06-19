# import pigpio
import gpiozero
from time import sleep
from playsound import playsound

import sys
import os

# プロジェクトのルートディレクトリを検索パスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.PicameraUtils import PicameraUtils

picamerautils = PicameraUtils()

# GPIOピン番号を指定
IR_PIN = 25

# pigpioライブラリの初期化
# pi = pigpio.pi()

# pi = gpiozero.DigitalInputDevice(IR_PIN)
pi = gpiozero.Button(IR_PIN, pull_up=None, active_state=True)

# if not pi.connected:
#     print("pigpioデーモンに接続できませんでした。")
#     exit()

# GPIOピンを入力モードに設定
# pi.set_mode(IR_PIN, pigpio.INPUT)

effect_path = "/home/rpiuser/opt/sounds/gundam_effect_newtype.mp3"

try:
    camFlg = False

    while True:
        # 赤外線センサーの状態を取得
        # sensor_state = pi.read(IR_PIN)
        # sensor_state = pi.is_active
        sensor_state = pi.value
        print(f"センサーの状態: {sensor_state}")

        if sensor_state == 1:
            camFlg = True
            print("そこっ！！")
            # カメラを起動
            picamerautils.start_preview()
            picamerautils.start_camera()
            # 赤外線センサーが反応した場合の処理
            playsound(effect_path)
            sleep(1)  # 1秒待機

        if sensor_state == 0:
            if camFlg:
                camFlg = False
                # カメラを停止
                picamerautils.stop_camera()
                picamerautils.reset_preview()
            # pigpioの終了処理
            # pi.stop()
        sleep(1)  # 1秒待機
except KeyboardInterrupt:
    print("\n終了します")
# finally:
    # pigpioの終了処理
    # pi.stop()
    