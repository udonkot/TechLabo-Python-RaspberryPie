import evdev
from evdev import InputDevice, categorize, ecodes
import threading

# デバイスのパスを指定（適宜変更）
JOYCON_DEVICE_PATH = "/dev/input/event9"  # Joy-Conのデバイスパス

def monitor_joycon():
    """Joy-Conの操作を監視"""
    try:
        joycon = InputDevice(JOYCON_DEVICE_PATH)
        print(f"Joy-Conが接続されました: {joycon.name}")
        
        # 加速度センサーのデータを初期化
        accel_x, accel_y, accel_z = 0, 0, 0

        for event in joycon.read_loop():
            if event.type == ecodes.EV_ABS:  # 加速度センサーやジャイロ操作
                if event.code == ecodes.ABS_X:
                    accel_x = event.value
                elif event.code == ecodes.ABS_Y:
                    accel_y = event.value
                elif event.code == ecodes.ABS_Z:
                    accel_z = event.value

                # 加速度センサーのデータを表示
                print(f"Joy-Con 加速度センサー: X={accel_x}, Y={accel_y}, Z={accel_z}")

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