import pigpio
import time
import random

# GPIOピンの設定
SERVO_PIN = 26

# pigpioの初期化
pi = pigpio.pi()

def set_angle(angle):
    """
    サーボモータを指定した角度に滑らかに動かす
    :param angle: 目標角度 (0～180度)
    """
    pulse_width = 500 + (angle / 180.0) * 2000  # パルス幅を計算 (500～2500μs)
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)

try:
    while True:
        # 0から180までの角度を順に動かす
        # for angle in range(0, 181, 5):
        #     print(f"Moving to {angle} degrees")
        #     set_angle(angle)
        #     time.sleep(1)
        # # 180から0までの角度を順に動かす
        # for angle in range(180, -1, -5):
        #     print(f"Moving to {angle} degrees")
        #     set_angle(angle)
        #     time.sleep(1)
        # # 0度に移動
        print("Move to 0 degrees")
        set_angle(0)
        time.sleep(random.random()+1)

        # # 90度に移動
        print("Move to 90 degrees")
        set_angle(90)
        time.sleep(random.random()+1)

        # # 180度に移動
        print("Move to 180 degrees")
        set_angle(180)
        time.sleep(random.random()+1)

        # # 90度に移動
        print("Move to 90 degrees")
        set_angle(90)
        time.sleep(random.random()+1)


except KeyboardInterrupt:
    print("終了します")
finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)  # サーボを停止
    pi.stop()