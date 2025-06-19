from picamera import PiCamera

from time import sleep


camera = PiCamera()
camera.start_preview(alph=192)
sleep(1)

camera.capture("/home/rpiuser/opt/photo/pic.jpg")
camera.stop_preview()
