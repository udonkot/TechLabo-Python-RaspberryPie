from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import pigpio
import os
import json
from pathlib import Path
import subprocess

# ===== 設定クラス =====
class Config:
    """設定を管理するクラス"""
    
    # Slack設定（環境変数から読み込み）
    SLACK_TOKEN = os.environ.get('SLACK_BOT_TOKEN', 'your-slack-token-here')
    SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#general')
    
    
    @classmethod
    def load_from_file(cls, filepath: str = 'config.json'):
        """JSONファイルから設定を読み込む"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config = json.load(f)
                for key, value in config.items():
                    setattr(cls, key, value)

# ===== Slack連携クラス =====
class SlackUploader():
    """Slack連携クラス"""
    
    def __init__(self):
        self.client = WebClient(token=Config.SLACK_TOKEN)
        
    def upload_image(self, filepath: str, message: str = "新しい写真を撮影しました！"):
        """画像をSlackにアップロード"""
        try:
            print(Config.SLACK_CHANNEL)
            with open(filepath, 'rb') as file:
                response = self.client.files_upload_v2(
                    channel=Config.SLACK_CHANNEL,
                    file=file,
                    initial_comment=message,
                    filename=os.path.basename(filepath)
                )
                return response['ok']
        except SlackApiError as e:
            print(f"Slackアップロードエラー: {e.response['error']}")
            return False
        except Exception as e:
            print(f"予期しないエラー: {e}")
            return False

def main():
    # 設定ファイルがあれば読み込み
    Config.load_from_file()

    slack = SlackUploader()
    slack.upload_image('./captures/capture_20250904_212013.jpg', 'テスト画像アップロード')

if __name__ == "__main__":
    main()


