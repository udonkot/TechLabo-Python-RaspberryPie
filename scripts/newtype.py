# import pigpio
from PIL import Image
import gpiozero
from time import sleep
from playsound import playsound

import sys
import os

# プロジェクトのルートディレクトリを検索パスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.PicameraUtils import PicameraUtils
from utils.DisplayUtils import DisplayUtils

picamerautils = PicameraUtils()
displayUtils = DisplayUtils()

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

displayUtils.lcd_init()

sinjinList = [
    'ｱｵｷ ﾎﾉｶ',
    'ｱｵｷ ﾘｮｳ',
    'ｱﾝﾄﾞｳｶｲ',
    'ｲｼﾔﾏ ﾋﾛﾑ',
    'ｶﾜｸﾞﾁ ﾀｲｷ',
    'ｺﾀﾞｲﾗ ﾘｮｳｽｹ',
    'ｻｶﾞﾜ ﾚｲ',
    'ﾄﾐﾅｶﾞ ﾐｷ',
    'ﾈﾓﾄ ﾕｳｷ',
    'ﾋﾄﾐ ﾀｶﾕｷ',
    'ｵｶﾞﾜ ｶｽﾞｷ',
    'ﾖｼﾀｹ ｼﾝ',
    'ﾌｼﾞﾀ ﾎﾅﾐ',
    'ﾏﾂﾓﾄ ｻﾔｶ',
    'ﾕｶﾜ ｶｽﾞﾀｶ',

]


try:
    camFlg = False

    # カメラを起動
    picamerautils.start_preview()
    picamerautils.start_camera()

    i = 0

    while True:
        if(i >= len(sinjinList)):
            i = 0

        displayUtils.lcd_message("WELCOME!", 0x80)  
        displayUtils.lcd_message(sinjinList[i] + "!!", 0xC0) 


        # 赤外線センサーの状態を取得
        sensor_state = pi.value
        print(f"センサーの状態: {sensor_state}")

        if sensor_state == 1:
            camFlg = True
            picamerautils.capture_file("picture.jpg")
            displayUtils.lcd_message("ｼﾝﾆｭｳｼｬ!", 0x80)  # LCDをクリア
            displayUtils.lcd_message("camera fire!", 0xC0)  # LCDをクリア
            # 赤外線センサーが反応した            # fire playsound(effect_path)

            img = Image.open("./picture.jpg")
            img.show()
            # sleep(1)  # 1秒待機

        if sensor_state == 0:
            if camFlg:
                camFlg = False
                # カメラを停止
                picamerautils.reset_preview()
                displayUtils.lcd_clear()
            # pigpioの終了処理
            # pi.stop()
        sleep(2)  # 1秒待機
        i += 1
except KeyboardInterrupt:
    picamerautils.stop_camera()
    print("\n終了します")
# finally:
    # pigpioの終了処理
    # pi.stop()
    