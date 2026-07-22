import os
from dotenv import load_dotenv

load_dotenv()

# Azure AI Vision (Computer Vision) - 物体・顔検出
VISION_ENDPOINT = os.getenv('AZURE_VISION_ENDPOINT', '').rstrip('/')
VISION_KEY = os.getenv('AZURE_VISION_KEY', '')

# Azure AI Speech - 音声合成
SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY', '')
SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION', '')
SPEECH_VOICE = os.getenv('AZURE_SPEECH_VOICE', 'ja-JP-NanamiNeural')
SPEECH_LANGUAGE = os.getenv('AZURE_SPEECH_LANGUAGE', 'ja-JP')

# カメラ・検出設定
CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
CAPTURE_INTERVAL_SEC = float(os.getenv('CAPTURE_INTERVAL_SEC', '5'))
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.6'))
