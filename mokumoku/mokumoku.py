import RPi.GPIO as GPIO
import time

# GPIO番号で指定（BCMモード）
GPIO_RED = 5      # 赤LED
GPIO_BLUE = 21     # 青LED
GPIO_GREEN = 26    # 緑LED
GPIO_YELLOW = 27   # 黄LED

def setup():
    """初期化"""
    GPIO.setmode(GPIO.BCM)  # GPIO番号モード
    GPIO.setwarnings(False)
    GPIO.setup(GPIO_RED, GPIO.OUT)
    GPIO.setup(GPIO_BLUE, GPIO.OUT)
    GPIO.setup(GPIO_GREEN, GPIO.OUT)
    GPIO.setup(GPIO_YELLOW, GPIO.OUT)
    # 青LEDは常時点灯
    GPIO.output(GPIO_BLUE, GPIO.OUT)

def main():
    print("=== LED点灯問題 (Raspberry Pi) ===")
    print("\nLEDの動作:")
    print("- 赤LED  : 1秒ごとに点灯/消灯")
    print("- 青LED  : 常時点灯")
    print("- 緑LED  : 0.5秒ごとに点灯（黄と交互）")
    print("- 黄LED  : 0.5秒ごとに点灯（緑と交互）")
    print(f"\n使用するGPIO番号:")
    print(f"- 赤  : GPIO{GPIO_RED}")
    print(f"- 青  : GPIO{GPIO_BLUE}")
    print(f"- 緑  : GPIO{GPIO_GREEN}")
    print(f"- 黄  : GPIO{GPIO_YELLOW}")
    print("\nプログラム開始... (Ctrl+Cで終了)\n")
    
    setup()
    
    red_state = False
    green_yellow_state = False  # False=緑ON, True=黄ON
    last_red_time = time.time()
    last_green_yellow_time = time.time()
    
    try:
        GPIO.output(GPIO_BLUE, GPIO.LOW)
        while True:
            current_time = time.time()
            
            # 赤LED: 1秒ごとに点灯/消灯
            if current_time - last_red_time >= 1.0:
                red_state = not red_state
                GPIO.output(GPIO_RED, GPIO.HIGH if red_state else GPIO.LOW)
                last_red_time = current_time
            
            # 緑/黄LED: 0.5秒ごとに交互点灯
            if current_time - last_green_yellow_time >= 0.5:
                green_yellow_state = not green_yellow_state
                GPIO.output(GPIO_GREEN, GPIO.LOW if green_yellow_state else GPIO.HIGH)
                GPIO.output(GPIO_YELLOW, GPIO.HIGH if green_yellow_state else GPIO.LOW)
                last_green_yellow_time = current_time
            
            time.sleep(0.01)  # CPU負荷軽減
            
    except KeyboardInterrupt:
        print("\n\nプログラムを終了します")
        GPIO.cleanup()

if __name__ == "__main__":
    main()
