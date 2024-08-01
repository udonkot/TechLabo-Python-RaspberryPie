import time
import RPi.GPIO as GPIO

# GPIOの初期化
def gpioSetup(gpioList):
    GPIO.setmode(GPIO.BCM)

    for gpioNum in gpioList:
        GPIO.setup(gpioNum, GPIO.OUT)

# 指定されたLEDを点灯
def lightsOn(gpioList):
    gpioSetup(gpioList)
    for gpioNum in gpioList:
        # なぜかHIGHLOWが逆に動作するので暫定対応
        # GPIO.output(gpioNum, GPIO.HIGH)
        GPIO.output(gpioNum, GPIO.LOW)

# 指定されたLEDを消灯
def lightsOff(gpioList):
    for gpioNum in gpioList:
        # なぜかHIGHLOWが逆に動作するので暫定対応
        # GPIO.output(gpioNum, GPIO.LOW)
        GPIO.output(gpioNum, GPIO.HIGH)

# LEDを点滅
def blinkLighting(gpioList, sleep, count):
    i = 0
    while i < count:
        singleLighting(gpioList, sleep)
        i = i+1

# LEDを交互に点灯
def alternateLighting(gpioList, sleep, count):
    i = 0
    while i < count:
        for gpioNum in gpioList:
            time.sleep(sleep)
            lightsOn([gpioNum])
            time.sleep(sleep)
            lightsOff([gpioNum])

        i = i+1

# 指定されたLEDを点灯して消灯
def allLighting(gpioList, sleep, count):
    i = 0
    while i < count:
        time.sleep(sleep)
        lightsOn(gpioList)
        time.sleep(sleep)
        lightsOff(gpioList)

        i = i+1

# 1つずつLEDを点灯して消灯
def singleLighting(gpioList, sleep):
    for gpioNum in gpioList:
        time.sleep(sleep)
        lightsOn([gpioNum])
        time.sleep(sleep)
        lightsOff([gpioNum])


