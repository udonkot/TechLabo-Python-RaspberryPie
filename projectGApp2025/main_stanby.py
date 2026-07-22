import time
import random
from hardware.led_controller import LEDController
import pigpio

def pwm_fade(led_controller, pin, start, end, step, delay):
    """
    指定したピンのLEDをPWM制御でフェードイン・フェードアウト
    :param led_controller: LEDControllerインスタンス
    :param pin: 制御するピン番号
    :param start: 開始のデューティサイクル（0～255）
    :param end: 終了のデューティサイクル（0～255）
    :param step: デューティサイクルの変化量
    :param delay: ステップ間の遅延（秒）
    """
    if start < end:
        duty_range = range(start, end + 1, step)
    else:
        duty_range = range(start, end - 1, -step)

    for duty in duty_range:
        led_controller.pi.set_PWM_dutycycle(pin, duty)
        time.sleep(delay)

def random_led_blink(led_controller, duration=10):
    """
    複数のLEDをランダムにPWM制御で点滅させるスクリプト
    :param led_controller: LEDControllerインスタンス
    :param duration: 実行時間（秒）
    """
    start_time = time.time()
    pins = list(led_controller.pins.values())  # LEDピンのリストを取得

    # while time.time() - start_time < duration:
    while True:
        # ランダムに点灯するピンを選択
        random_pins = random.sample(pins, random.randint(1, len(pins)))
        print(f"選択されたピン: {random_pins}")  # デバッグ出力

        # 選択したピンをゆっくり点灯
        for pin in random_pins:
            if isinstance(pin, int):  # ピンが整数であることを確認
                pwm_fade(led_controller, pin, start=0, end=255, step=5, delay=0.02)
            else:
                print(f"無効なピン: {pin}")  # デバッグ出力

        time.sleep(2)  # 2秒間点灯

        # 選択したピンをゆっくり消灯
        for pin in random_pins:
            if isinstance(pin, int):  # ピンが整数であることを確認
                pwm_fade(led_controller, pin, start=255, end=0, step=5, delay=0.02)
            else:
                print(f"無効なピン: {pin}")  # デバッグ出力

        time.sleep(2)  # 2秒間消灯

if __name__ == "__main__":
    pi = pigpio.pi()  # pigpioインスタンスを作成
    led_controller = LEDController(pi)

    try:
        random_led_blink(led_controller, duration=20)  # 20秒間ランダム点滅
    except KeyboardInterrupt:
        print("終了します")
    finally:
        led_controller.all_off()  # すべてのLEDを消灯
        pi.stop()