import evdev
from evdev import InputDevice, categorize, ecodes
import threading
import math

# デバイスのパスを指定（適宜変更）
JOYCON_DEVICE_PATH = "/dev/input/event9"  # Joy-Conのデバイスパス

def calculate_tilt(x, y, z):
    """ジャイロデータから傾きを計算"""
    try:
        pitch = math.atan2(y, math.sqrt(x**2 + z**2)) * (180 / math.pi)
        roll = math.atan2(-x, z) * (180 / math.pi)
        return pitch, roll
    except ZeroDivisionError:
        return 0, 0

def monitor_joycon():
    """Joy-Conの操作を監視"""
    try:
        joycon = InputDevice(JOYCON_DEVICE_PATH)
        print(f"Joy-Conが接続されました: {joycon.name}")
        x, y, z = 0, 0, 0  # ジャイロデータの初期値

        for event in joycon.read_loop():
            if event.type == ecodes.EV_ABS:  # ジャイロ操作
                if event.code == ecodes.ABS_X:
                    x = event.value
                elif event.code == ecodes.ABS_Y:
                    y = event.value
                elif event.code == ecodes.ABS_Z:
                    z = event.value

                # 傾きを計算
                pitch, roll = calculate_tilt(x, y, z)
                print(f"Joy-Con 傾き: Pitch={pitch:.2f}°, Roll={roll:.2f}°")

            elif event.type == ecodes.EV_KEY:  # ボタン操作
                key_event = categorize(event)
                print(f"Joy-Con ボタン操作: {key_event}")

    except FileNotFoundError:
        print("Joy-Conが見つかりませんでした。デバイスパスを確認してください。")

def main():
    joycon_thread = threading.Thread(target=monitor_joycon)
    joycon_thread.start()
    joycon_thread.join()

if __name__ == "__main__":
    main()