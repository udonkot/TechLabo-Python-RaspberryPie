import time

import config
from camera_capture import CameraCapture
from vision_analyzer import VisionAnalyzer
from speech_speaker import SpeechSpeaker


def build_message(result):
    parts = []
    if result['objects']:
        parts.append('{}を検出しました'.format('、'.join(result['objects'])))
    if result['face_count'] > 0:
        parts.append(f"顔を{result['face_count']}個検出しました")

    if not parts:
        return None
    return '。'.join(parts) + '。'


def main():
    camera = CameraCapture(config.CAMERA_INDEX)
    vision = VisionAnalyzer(config.VISION_ENDPOINT, config.VISION_KEY)
    speaker = SpeechSpeaker(
        config.SPEECH_KEY, config.SPEECH_REGION,
        config.SPEECH_VOICE, config.SPEECH_LANGUAGE,
    )

    print('物体・顔識別を開始します。Ctrl+Cで終了します。')
    last_message = None

    try:
        while True:
            try:
                image_bytes = camera.capture_jpeg_bytes()
                result = vision.analyze(image_bytes, config.CONFIDENCE_THRESHOLD)
                message = build_message(result)

                if message and message != last_message:
                    print(message)
                    speaker.speak(message)
                    last_message = message
                elif not message:
                    last_message = None

            except Exception as e:
                print(f'識別処理でエラーが発生しました: {e}')

            time.sleep(config.CAPTURE_INTERVAL_SEC)

    except KeyboardInterrupt:
        print('終了します')
    finally:
        camera.release()


if __name__ == '__main__':
    main()
