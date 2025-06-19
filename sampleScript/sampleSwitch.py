import RPi.GPIO as GPIO
import time

# GPIOピンの設定
SWITCH_PIN = 18  # スライドスイッチの接続先

# GPIOの初期化
GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # プルアップ抵抗を有効化

try:
    while True:
        # スライドスイッチの状態を読み取る
        switch_state = GPIO.input(SWITCH_PIN)
        if switch_state == GPIO.LOW:
            print("スイッチがONです")
        else:
            print("スイッチがOFFです")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("終了します")
finally:
    GPIO.cleanup()