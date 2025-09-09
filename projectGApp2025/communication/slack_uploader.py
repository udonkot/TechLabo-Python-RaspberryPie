#!/usr/bin/env python3
"""
Slack連携クラス
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from ..config import Config
from ..config import RobotComponent


class SlackUploader(RobotComponent):
    """Slack連携クラス"""
    
    def __init__(self, pi):
        super().__init__("Slack Uploader", pi)
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
