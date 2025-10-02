import time
import random
from hardware.led_controller import LEDController
import pigpio

def random_led_blink(led_controller, duration=10):
    """
    複数のLEDをランダムに点滅させるスクリプト
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

        # 選択したピンを点灯
        for pin in random_pins:
            if isinstance(pin, int):  # ピンが整数であることを確認
                led_controller.pi.write(pin, 1)
            else:
                print(f"無効なピン: {pin}")  # デバッグ出力

        time.sleep(2)  # 2秒間点灯

        # 選択したピンを消灯
        for pin in random_pins:
            if isinstance(pin, int):  # ピンが整数であることを確認
                led_controller.pi.write(pin, 0)
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