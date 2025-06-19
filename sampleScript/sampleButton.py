import RPi.GPIO as GPIO
import time

# GPIOピンの設定
LED_PIN = 20  # Replace with your LED GPIO pin
BUTTON_PIN = 21  # Replace with your button GPIO pin

# GPIOの初期化
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# LEDの状態を管理する変数
led_state = False

def toggle_led(channel):
    global led_state
    led_state = not led_state
    GPIO.output(LED_PIN, led_state)

# ボタンのイベント検出を設定
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=toggle_led, bouncetime=200)

try:
    print("ボタンを押してライトをオン/オフしてください (Ctrl+Cで終了)")
    while True:
        time.sleep(0.1)  # CPU使用率を下げるためのスリープ
except KeyboardInterrupt:
    print("\n終了します")
finally:
    GPIO.output(LED_PIN, GPIO.LOW)  # LEDをオフにする
    GPIO.cleanup()
