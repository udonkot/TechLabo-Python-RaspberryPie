from pathlib import Path

import cv2
import face_recognition
import numpy as np


class FaceIdentifier:
    """あらかじめ登録した顔写真(known_faces/<名前>/*)と照合し、人物名を特定する

    Azureは使わず、Raspberry Pi上でface_recognition(dlib)によりローカルで処理する。
    """

    def __init__(self, known_faces_dir, tolerance=0.6):
        self.tolerance = tolerance
        self.known_encodings = []
        self.known_names = []
        self._load_known_faces(Path(known_faces_dir))

    def _load_known_faces(self, known_faces_dir):
        if not known_faces_dir.exists():
            return

        for person_dir in sorted(known_faces_dir.iterdir()):
            if not person_dir.is_dir():
                continue

            name = person_dir.name
            for image_path in sorted(person_dir.glob('*')):
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(name)

    def identify_names(self, image_bytes):
        if not self.known_encodings:
            return []

        array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        names = []
        for face_encoding in face_encodings:
            distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            best_index = int(np.argmin(distances))
            if distances[best_index] <= self.tolerance:
                names.append(self.known_names[best_index])

        return names
