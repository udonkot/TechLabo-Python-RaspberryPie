import evdev
from evdev import InputDevice, categorize, ecodes
import threading
import pigpio
import time
import random


# デバイスのパスを指定（適宜変更）
JOYCON_DEVICE_PATH = "/dev/input/event9"  # Joy-Conのデバイスパス
WIIMOTE_DEVICE_PATH = "/dev/input/event8"  # Wiiリモコンのデバイスパス

def monitor_joycon():
    """Joy-Conの操作を監視"""
    try:
        joycon = InputDevice(JOYCON_DEVICE_PATH)
        print(f"Joy-Conが接続されました: {joycon.name}")
        for event in joycon.read_loop():
            if event.type == ecodes.EV_ABS:  # ジャイロ操作
                abs_event = categorize(event)
                print(f"Joy-Con ジャイロ操作: {abs_event}")
            elif event.type == ecodes.EV_KEY:  # ボタン操作
                key_event = categorize(event)
                print(f"Joy-Con ボタン操作: {key_event}")
    except FileNotFoundError:
        print("Joy-Conが見つかりませんでした。デバイスパスを確認してください。")

def monitor_wiimote():
    """Wiiリモコンの操作を監視"""
    try:
        wiimote = InputDevice(WIIMOTE_DEVICE_PATH)
        print(f"Wiiリモコンが接続されました: {wiimote.name}")
        for event in wiimote.read_loop():
            if event.type == ecodes.EV_KEY:  # ボタン操作
                key_event = categorize(event)
                print(f"Wiiリモコン ボタン操作: {key_event}")
                print(key_event.keycode)
                print(key_event.keystate)
                if key_event.keycode == 'KEY_UP' and key_event.keystate == 0:
                    # 左向く
                    print("モーター回転")
                    round_motor(-45)
                if key_event.keycode == 'KEY_DOWN' and key_event.keystate == 0:
                    # 右向く
                    print("モーター回転")
                    round_motor(45)
                # if key_event.keycode == 'BTN_2' and key_event.keystate == 0:
                #     # モーター回転
                #     print("モーター回転")
                #     round_motor(90)
            elif event.type == ecodes.EV_ABS:  # モーション操作
                abs_event = categorize(event)
                print(f"Wiiリモコン モーション操作: {abs_event}")
    except FileNotFoundError:
        print("Wiiリモコンが見つかりませんでした。デバイスパスを確認してください。")

def set_angle(angle):
    """
    サーボモータを指定した角度に滑らかに動かす
    :param angle: 目標角度 (0～180度)
    """
    pulse_width = 500 + (angle / 180.0) * 2000  # パルス幅を計算 (500～2500μs)
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)

def round_motor(changeAngle):
    global reverse, angle
    # if reverse == True:
    #     angle = angle - changeAngle
    #     if 180 < angle : angle = 180
    # else:
    #     angle = angle + changeAngle
    #     if angle < 0 : angle = 0

    # print("Move to" + angle.__str__() + "degrees")
    # set_angle(angle)

    # if 180 <= angle : reverse = True
    # if angle <= 0 : reverse = False

    if angle + changeAngle >= 180 : return
    if angle + changeAngle <= 0 : return

    angle = angle + changeAngle

    print("Move to" + angle.__str__() + "degrees")
    set_angle(angle)



# GPIOピンの設定
SERVO_PIN = 26

# pigpioの初期化
pi = pigpio.pi()

reverse = False
angle = 90
set_angle(angle)



def main():
    # Joy-ConとWiiリモコンの監視を並行して実行
    joycon_thread = threading.Thread(target=monitor_joycon)
    wiimote_thread = threading.Thread(target=monitor_wiimote)

    joycon_thread.start()
    wiimote_thread.start()

    joycon_thread.join()
    wiimote_thread.join()

if __name__ == "__main__":
    main()