import time

import cv2

try:
    from picamera2 import Picamera2
except Exception:
    # 未インストールに加え、numpyのABI不一致等でもここに落ちてくる。
    # backend='opencv'利用時にpicamera2が壊れていても起動できるようにする。
    Picamera2 = None


class CameraCapture:
    """接続されたカメラ(USBカメラ/PiCamera)から画像を取得する

    backend='opencv'    : USBウェブカメラなど、V4L2で直接読めるカメラ向け
    backend='picamera2' : Raspberry Pi Camera Module(CSI, libcameraスタック)向け
    """

    def __init__(self, camera_index=0, backend='opencv'):
        self.backend = backend

        if backend == 'picamera2':
            if Picamera2 is None:
                raise RuntimeError(
                    'picamera2がインストールされていません。'
                    'sudo apt install -y python3-picamera2 を実行し、'
                    'venvは --system-site-packages で作り直してください'
                )
            self.picam2 = Picamera2()
            still_config = self.picam2.create_still_configuration(
                main={'size': (1280, 720)}
            )
            self.picam2.configure(still_config)
            self.picam2.start()
            # 自動露出・ホワイトバランスが安定するまで待つ
            time.sleep(2)
        else:
            self.capture = cv2.VideoCapture(camera_index)
            if not self.capture.isOpened():
                raise RuntimeError(f'カメラ(index={camera_index})を開けませんでした')

    def capture_jpeg_bytes(self):
        if self.backend == 'picamera2':
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            ok, frame = self.capture.read()
            if not ok:
                raise RuntimeError('カメラからのフレーム取得に失敗しました')

        ok, buffer = cv2.imencode('.jpg', frame)
        if not ok:
            raise RuntimeError('JPEGエンコードに失敗しました')

        return buffer.tobytes()

    def release(self):
        if self.backend == 'picamera2':
            self.picam2.stop()
        else:
            self.capture.release()
