# projectGApp2026 - Azure物体・顔識別音声応答

Raspberry Pi 4に接続したカメラの映像をAzure AI Visionで解析し、検出した物体・顔をAzure AI Speechで音声応答するスクリプトです。

## 構成

- `main.py` : メインループ(撮影→識別→音声応答)
- `camera_capture.py` : カメラからのフレーム取得
- `vision_analyzer.py` : Azure AI Vision (Computer Vision) での物体・顔検出
- `speech_speaker.py` : Azure AI Speech での音声合成・再生
- `config.py` : `.env` から設定を読み込み

## 必要なAzureリソース

1. Azure AI Vision (Computer Vision) リソースを作成し、エンドポイントとキーを取得
2. Azure AI Speech リソースを作成し、キーとリージョンを取得

## セットアップ (Raspberry Pi OS)

```bash
sudo apt update
sudo apt install -y libasound2 libssl-dev build-essential
```

### USBウェブカメラの場合

`/dev/video0` として認識されているか確認してください。`.env`は `CAMERA_BACKEND=opencv` のままでOKです。

```bash
ls /dev/video*
```

### Raspberry Pi Camera Module(CSIリボンケーブル接続)の場合

Bullseye以降のRaspberry Pi OSはlibcameraスタックが標準のため、
OpenCVの`cv2.VideoCapture`では映像を取得できず起動時にハングすることがあります。
`rpicam-hello` / `libcamera-hello` でカメラが映ることを確認したら、
`.env`で `CAMERA_BACKEND=picamera2` を指定し、picamera2を使ってください。

```bash
sudo apt install -y python3-picamera2
```

picamera2はシステムパッケージなので、venvは `--system-site-packages` を付けて作成してください。

```bash
python -m venv --system-site-packages venv
source ./venv/bin/activate
pip install -r requirements.txt
```

USBカメラのみを使う場合は通常のvenvで構いません。

```bash
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

`.env.example` を `.env` にコピーし、Azureのキー・エンドポイントを設定してください。

```bash
cp .env.example .env
```

## 実行

```bash
python main.py
```

Ctrl+Cで終了します。`CAPTURE_INTERVAL_SEC` (既定5秒)ごとに撮影・識別を行い、
直前と異なる検出結果が得られたときのみ音声で応答します。
