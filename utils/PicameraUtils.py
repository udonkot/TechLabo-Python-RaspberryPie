from picamera2 import Picamera2, Preview
import libcamera
import time

# classの説明
# PicameraUtilsは、Raspberry Piのカメラを操作するためのユーティリティクラスです。
# このクラスは、カメラの設定、プレビューの開始、写真の撮影、およびカメラの停止を行います。
class PicameraUtils:

    PICTURE_WIDTH = 1920
    PICTURE_HEIGHT = 1080
    SAVE_DIR = "./"

    cam_no = 0  # 使用するカメラ番号
    width = 1920
    height = 1080

    flip_hor = False
    flip_ver = False

    wait_time = 5

    save_file = "picture.jpg"

    # カメラ情報を取得してカメラ番号を確認
    picam2 = Picamera2()
    camera_info = Picamera2.global_camera_info()

    if cam_no >= len(camera_info):
        raise IndexError(f"指定されたカメラ番号 {cam_no} は存在しません。利用可能なカメラ: {len(camera_info)}")

    # カメラの設定
    preview_config = picam2.create_preview_configuration(main={"size": (PICTURE_WIDTH, PICTURE_HEIGHT)})
    preview_config["transform"] = libcamera.Transform(hflip=flip_hor, vflip=flip_ver)

    picam2.configure(preview_config)

    # # プレビューを開始
    # picam2.start_preview(Preview.QTGL)


    def __init__(self):
        pass

    def start_camera(self):
        # カメラを開始
        self.picam2.start()
        time.sleep(self.wait_time)
        # # カメラを開始
        # picam2.start()
        # time.sleep(wait_time)

    def stop_camera(self):
        # カメラを停止
        self.picam2.stop()
    
    def start_preview(self):
        # プレビューを開始
        self.picam2.start_preview(Preview.QTGL)
        
    def reset_preview(self):
        # プレビューをリセット
        self.picam2.stop_preview()
        self.picam2.start_preview(Preview.QTGL)

    def capture_file(self, save_file):
        # 写真を保存
        self.picam2.capture_file(save_file)
        print(f"写真を保存しました: {save_file}")

        # # 写真を保存
        # picam2.capture_file(save_file)
        # print(f"写真を保存しました: {save_file}")

