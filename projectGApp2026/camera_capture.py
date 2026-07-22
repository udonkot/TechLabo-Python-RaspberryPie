import cv2


class CameraCapture:
    """接続されたカメラ(USBカメラ/PiCamera)から画像を取得する"""

    def __init__(self, camera_index=0):
        self.capture = cv2.VideoCapture(camera_index)
        if not self.capture.isOpened():
            raise RuntimeError(f'カメラ(index={camera_index})を開けませんでした')

    def capture_jpeg_bytes(self):
        ok, frame = self.capture.read()
        if not ok:
            raise RuntimeError('カメラからのフレーム取得に失敗しました')

        ok, buffer = cv2.imencode('.jpg', frame)
        if not ok:
            raise RuntimeError('JPEGエンコードに失敗しました')

        return buffer.tobytes()

    def release(self):
        self.capture.release()
