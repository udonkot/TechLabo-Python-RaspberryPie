import RPi.GPIO as GPIO
import time
# import rpicamera2
# import picamera2p
from picamera2 import Picamera2, Preview

import libcamera

from time import sleep

PICTURE_WIDTH = 800
PICTURE_HEIGHT = 600
SAVE_DIR = "./"

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

cam_no = 0
width = 1920
height = 1080

flip_hor = False
flip_ver = False

wait_time = 5

save_file = "picture.jpg"

picam2 = Picamera2()
#picam2 = picamera2.Picamera2( camera_num = cam_no)

preview_config = picam2.create_preview_configuration(main={"size": (PICTURE_WIDTH, PICTURE_HEIGHT)})
preview_config["transform"] = libcamera.Transform(hflip=flip_hor, vflip=flip_ver)

picam2.configure(preview_config)

picam2.start_preview( Preview.QTGL)
picam2.start()


try:
    while True:
        if GPIO.input(21) == GPIO.LOW:  # ボタンが押された場合
            # print("Button pressed")
            # GPIO20のライトオン
            GPIO.setup(20, GPIO.OUT)
            # カメラで撮影

            # time.sleep(wait_time)

            # picam2.capture_file(save_file)

            st = time.time()
            filename = time.strftime("%Y%m%d_%H%M%S") + ".jpg"
            # picam2.capture_file(SAVE_DIR + filename)

            print("fire!")
            sleep(1)
            picam2.close()
            GPIO.setup(20, GPIO.IN)

            break
        else :
            # print("Button released")
            # GPIO20のライトオフ
            GPIO.setup(20, GPIO.IN)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting program")
finally:
    GPIO.cleanup()  # GPIOピンをクリーンアップ