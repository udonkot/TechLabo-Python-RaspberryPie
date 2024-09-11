import subprocess
import sys

def play_video(video_path):
    # VLCを起動して動画を再生
    subprocess.run(['vlc', video_path])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python play_video.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    play_video(video_path)
