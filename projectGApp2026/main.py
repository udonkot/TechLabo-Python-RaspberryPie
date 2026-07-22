import time
from pathlib import Path

import config
from camera_capture import CameraCapture
from vision_analyzer import VisionAnalyzer
from speech_speaker import SpeechSpeaker
from face_identifier import FaceIdentifier

CAPTURES_DIR = Path(__file__).parent / 'captures'


def build_message(result, face_names):
    parts = []
    if result['objects']:
        parts.append('{}を検出しました'.format('、'.join(result['objects'])))

    if face_names:
        parts.append('{}を検出しました'.format('、'.join(face_names)))
    elif result['face_count'] > 0:
        parts.append(f"顔を{result['face_count']}個検出しました")

    if not parts:
        return None
    return '。'.join(parts) + '。'


def main():
    camera = CameraCapture(config.CAMERA_INDEX, config.CAMERA_BACKEND)
    vision = VisionAnalyzer(config.VISION_ENDPOINT, config.VISION_KEY)
    speaker = SpeechSpeaker(
        config.SPEECH_KEY, config.SPEECH_REGION,
        config.SPEECH_VOICE, config.SPEECH_LANGUAGE,
    )

    face_identifier = FaceIdentifier(config.KNOWN_FACES_DIR, config.FACE_MATCH_TOLERANCE)
    registered_count = len(set(face_identifier.known_names))
    if registered_count > 0:
        print(f'顔認識: {registered_count}人を登録済みです。', flush=True)
    else:
        print(
            f'顔認識: {config.KNOWN_FACES_DIR} に登録済みの人物がいません。'
            'enroll_person.pyで登録できます。',
            flush=True,
        )

    print('物体・顔識別を開始します。Ctrl+Cで終了します。', flush=True)
    last_message = None

    try:
        while True:
            try:
                print('撮影中...', flush=True)
                image_bytes = camera.capture_jpeg_bytes()

                CAPTURES_DIR.mkdir(exist_ok=True)
                (CAPTURES_DIR / 'last_frame.jpg').write_bytes(image_bytes)

                print('Azure Visionで解析中...', flush=True)
                result = vision.analyze(image_bytes, config.CONFIDENCE_THRESHOLD)
                print(f'解析結果: {result}', flush=True)

                face_names = []
                if result['face_count'] > 0:
                    print('ローカルで顔照合中...', flush=True)
                    face_names = face_identifier.identify_names(image_bytes)
                    print(f'照合結果: {face_names}', flush=True)

                message = build_message(result, face_names)

                if message and message != last_message:
                    print(message)
                    speaker.speak(message)
                    last_message = message
                elif not message:
                    print('検出なし')
                    last_message = None

            except Exception as e:
                print(f'識別処理でエラーが発生しました: {e}', flush=True)

            time.sleep(config.CAPTURE_INTERVAL_SEC)

    except KeyboardInterrupt:
        print('終了します')
    finally:
        camera.release()


if __name__ == '__main__':
    main()
