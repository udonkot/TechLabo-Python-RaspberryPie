"""
ローカル顔認識(face_recognition)用の人物登録スクリプト。

使い方:
    python enroll_person.py <名前> <顔写真1> [顔写真2] ...

例:
    python enroll_person.py 山田太郎 photos/yamada_1.jpg photos/yamada_2.jpg

known_faces/<名前>/ ディレクトリに写真をコピーする。
main.py起動時に自動でこのディレクトリを読み込んで顔を照合できるようにする。
"""

import shutil
import sys
from pathlib import Path

import config


def main():
    if len(sys.argv) < 3:
        print('使い方: python enroll_person.py <名前> <顔写真1> [顔写真2] ...')
        sys.exit(1)

    name = sys.argv[1]
    image_paths = [Path(p) for p in sys.argv[2:]]

    person_dir = Path(config.KNOWN_FACES_DIR) / name
    person_dir.mkdir(parents=True, exist_ok=True)

    for image_path in image_paths:
        destination = person_dir / image_path.name
        shutil.copy(image_path, destination)
        print(f'登録しました: {destination}')

    print(f'"{name}" の登録が完了しました。main.py実行時に自動で読み込まれます。')


if __name__ == '__main__':
    main()
