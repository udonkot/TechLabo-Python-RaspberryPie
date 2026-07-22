import requests


class VisionAnalyzer:
    """Azure AI Vision (Computer Vision) で画像内の物体・顔を検出する"""

    def __init__(self, endpoint, key):
        if not endpoint or not key:
            raise ValueError('AZURE_VISION_ENDPOINT / AZURE_VISION_KEY が設定されていません')

        self.analyze_url = f'{endpoint}/vision/v3.2/analyze'
        self.headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/octet-stream',
        }
        self.params = {'visualFeatures': 'Objects,Faces'}

    def analyze(self, image_bytes, confidence_threshold=0.6):
        response = requests.post(
            self.analyze_url,
            headers=self.headers,
            params=self.params,
            data=image_bytes,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()

        objects = [
            obj['object']
            for obj in result.get('objects', [])
            if obj.get('confidence', 0) >= confidence_threshold
        ]
        face_count = len(result.get('faces', []))

        return {'objects': objects, 'face_count': face_count}
