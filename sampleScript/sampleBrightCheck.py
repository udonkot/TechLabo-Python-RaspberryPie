import RPi.GPIO as GPIO
import time

# GPIOピンの設定
PHOTO_PIN = 26  # フォトトランジスタの接続先

# GPIOの初期化
GPIO.setmode(GPIO.BCM)
GPIO.setup(PHOTO_PIN, GPIO.IN)

try:
    while True:
        # フォトトランジスタの状態を読み取る
        light_detected = GPIO.input(PHOTO_PIN)
        if light_detected:
            print("光が検出されました")
        else:
            print("光が検出されていません")
        time.sleep(1)

except KeyboardInterrupt:
    print("終了します")
finally:
    GPIO.cleanup()