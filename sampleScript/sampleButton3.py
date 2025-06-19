import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# GPIO20を出力モードに設定,初期値消灯
GPIO.setup(26, GPIO.OUT)  # GPIO26を出力モードに設定
GPIO.output(26, GPIO.HIGH)  # GPIO26を消灯
GPIO.setup(19, GPIO.OUT)  # GPIO19を出力モードに設定
GPIO.output(19, GPIO.HIGH)  # GPIO19を消灯
GPIO.setup(13, GPIO.OUT)  # GPIO13を出力モードに設定
GPIO.output(13, GPIO.HIGH)  # GPIO13を消灯
GPIO.setup(6, GPIO.OUT)  # GPIO6を出力モードに設定
GPIO.output(6, GPIO.HIGH)  # GPIO6を消灯

# 交互に点灯する関数
def blink_led(pattern):
    match pattern:
        case 1:
            GPIO.output(26, GPIO.LOW)  # LEDを点灯
            GPIO.output(19, GPIO.HIGH)  # LEDを点灯
            GPIO.output(13, GPIO.HIGH)  # LEDを点灯
            GPIO.output(6, GPIO.HIGH)  # LEDを点灯
        case 2:
            GPIO.output(26, GPIO.HIGH)  # LEDを点灯
            GPIO.output(19, GPIO.LOW)  # LEDを点灯
            GPIO.output(13, GPIO.HIGH)  # LEDを点灯
            GPIO.output(6, GPIO.HIGH)  # LEDを点灯
        case 3:
            GPIO.output(26, GPIO.HIGH)  # LEDを点灯
            GPIO.output(19, GPIO.HIGH)  # LEDを点灯
            GPIO.output(13, GPIO.LOW)  # LEDを点灯
            GPIO.output(6, GPIO.HIGH)  # LEDを点灯
        case 4:
            GPIO.output(26, GPIO.HIGH)  # LEDを点灯
            GPIO.output(19, GPIO.HIGH)  # LEDを点灯
            GPIO.output(13, GPIO.HIGH)  # LEDを点灯
            GPIO.output(6, GPIO.LOW)  # LEDを点灯
        case _:
            pass


try:
    count = 0
    i = 1
    roulatteflg = False
    restalrtFlg = False
    while True:
        if GPIO.input(16) == GPIO.LOW:  # ボタンが押された場合
            if roulatteflg == False:
                count += 1
            restalrtFlg = True
            roulatteflg = True
        else:
            roulatteflg = False

        if roulatteflg == False and restalrtFlg == False:
            continue
        
        if roulatteflg == True:
            #print("Button pressed")
            # GPIO20のライトオン
            blink_led(i)
            time.sleep(0.05)  # 点灯時間
            i += 1
            if i > 4:
                i = 1
        else:
            # GPIO13が点灯していたらあたり
            if GPIO.input(13) == GPIO.LOW:
                print("当たり!!")
                break
    
    # 当たるまでのcountを表示
    print(f"当たるまでの回数: {count}")
    input()

except KeyboardInterrupt:
    print("Exiting program")
finally:
    GPIO.cleanup()  # GPIOピンをクリーンアップ

