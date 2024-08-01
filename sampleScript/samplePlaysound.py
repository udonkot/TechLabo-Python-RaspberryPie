import os
import sys
from playsound import playsound
from dotenv import load_dotenv

load_dotenv()

def main(music_file_path):
    print('start : ' + music_file_path)
    playsound(music_file_path)

if __name__ == "__main__":

    args = sys.argv
    if 2 == len(args):
        music_file_path = args[1]
    else:
        music_file_path = os.getenv('SOUND_DIR') + 'Side_Left.wav'

    main(music_file_path)
