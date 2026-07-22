# projectGApp2026 - Azure物体・顔識別音声応答

Raspberry Pi 4に接続したカメラの映像をAzure AI Visionで解析し、検出した物体・顔をAzure AI Speechで音声応答するスクリプトです。
人物の個人識別(誰の顔か)はAzureを使わず、Raspberry Pi上でローカルに`face_recognition`で処理します。

## 構成

- `main.py` : メインループ(撮影→識別→音声応答)
- `camera_capture.py` : カメラからのフレーム取得
- `vision_analyzer.py` : Azure AI Vision (Computer Vision) での物体・顔検出
- `face_identifier.py` : `face_recognition`(dlib)による人物の個人識別(誰の顔か)。Raspberry Pi上でローカルに処理し、Azureは使わない
- `enroll_person.py` : 認識させたい人物の顔写真を`known_faces/`に登録するスクリプト
- `speech_speaker.py` : Azure AI Speech での音声合成・再生
- `config.py` : `.env` から設定を読み込み

## 必要なAzureリソース

1. Azure AI Vision (Computer Vision) リソースを作成し、エンドポイントとキーを取得
2. Azure AI Speech リソースを作成し、キーとリージョンを取得

人物の名前を識別する機能(誰の顔か)はAzureを使わず、Raspberry Pi上で
`face_recognition`ライブラリによりローカルに処理する。Azure Face APIの
Limited Access申請は不要。

### 人物の登録手順(ローカル顔認識)

1. 認識させたい人物ごとに、複数枚(できれば正面・別角度)の顔写真を用意
2. 人物ごとに登録スクリプトを実行(`known_faces/<名前>/`に写真がコピーされる)

   ```bash
   python enroll_person.py 山田太郎 photos/yamada_1.jpg photos/yamada_2.jpg
   ```

3. `main.py`起動時に`known_faces/`以下が自動的に読み込まれ、以後の撮影で
   顔が一致した人物の名前を読み上げる。写真を追加・変更した場合は
   `main.py`を再起動すれば反映される。

### 処理負荷について(Raspberry Pi 4)

`face_recognition`の顔検出・照合はCPUのみで動作し、GPUは不要。
5秒間隔(既定の`CAPTURE_INTERVAL_SEC`)のような低頻度のポーリングであれば
Pi 4(2GB以上のモデル推奨)で問題なく動作する。1フレームあたりの処理は
概ね1〜2秒程度で、リアルタイム動画のような高フレームレートを要求しなければ
性能面のボトルネックにはならない。

## セットアップ (Raspberry Pi OS)

```bash
sudo apt update
sudo apt install -y libasound2 libssl-dev build-essential cmake libopenblas-dev liblapack-dev
```

`cmake`・`libopenblas-dev`・`liblapack-dev`は`face_recognition`が依存する`dlib`のビルドに使う。
Raspberry Pi OSのpipはpiwheels(ARM向けプリビルドwheel置き場)を参照する設定になっているため、
通常はソースからのビルドは走らず数分で終わるはず。piwheelsに対応wheelがない場合は
ソースビルドとなり数十分かかることがある。

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
sudo apt install -y python3-picamera2 python3-opencv python3-numpy
```

picamera2・opencv・numpyはすべてシステムパッケージ(apt版)を使い、
venvは `--system-site-packages` を付けて作成してください。
`requirements.txt` の `opencv-python` をpipで入れてしまうと、
apt版とはABIが異なるnumpyがvenv内にインストールされ、
`ValueError: numpy.dtype size changed, may indicate binary incompatibility`
のようなエラーでpicamera2/simplejpegが起動時にクラッシュします。

```bash
python -m venv --system-site-packages venv
source ./venv/bin/activate
pip install requests python-dotenv azure-cognitiveservices-speech face_recognition
```

(`opencv-python`と`numpy`は上記コマンドでは意図的に入れていません。venvが
`--system-site-packages`のため、aptで入れたものがそのまま使われます)

もし既にvenv内へ`opencv-python`や`numpy`をpipでインストールしてしまっている場合は、
削除してからaptの方を使うようにしてください。

```bash
pip uninstall -y opencv-python opencv-python-headless numpy
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
