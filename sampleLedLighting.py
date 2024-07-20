import time
import RPi.GPIO as GPIO

LIGHT_GROUP_ALL = [17,27,26,16,20,21,19,13,6]
#LIGHT_GROUP_ALL = [16,20,21]
LIGHT_GROUP_A = [17,27,26]
LIGHT_GROUP_B = [16,20,21]
LIGHT_GROUP_C = [19,13,6]

LIGHT_GROUP_RED = [17,21,19]
LIGHT_GROUP_GREEN = [26,20,6]
LIGHT_GROUP_YELLOW = [27,16,13]


def init():
    GPIO.setmode(GPIO.BCM)
    gpioSetup(LIGHT_GROUP_ALL)
    lightsOff(LIGHT_GROUP_ALL)

def gpioSetup(gpioList):
    for gpioNum in gpioList:
        GPIO.setup(gpioNum, GPIO.OUT)

def lightsOn(gpioList):
    for gpioNum in gpioList:
        # なぜかHIGHLOWが逆に動作するので暫定対応
        # GPIO.output(gpioNum, GPIO.HIGH)
        GPIO.output(gpioNum, GPIO.LOW)

def lightsOff(gpioList):
    for gpioNum in gpioList:
        # なぜかHIGHLOWが逆に動作するので暫定対応
        # GPIO.output(gpioNum, GPIO.LOW)
        GPIO.output(gpioNum, GPIO.HIGH)

def blinkLighting(gpioList, sleep, count):
    i = 0
    while i < count:
        singleLighting(gpioList, sleep)
        i = i+1

def alternateLighting(gpioList, sleep, count):
    i = 0
    while i < count:
        for gpioNum in gpioList:
            time.sleep(sleep)
            lightsOn([gpioNum])
            time.sleep(sleep)
            lightsOff([gpioNum])

        i = i+1


def allLighting(gpioList, sleep):
    time.sleep(sleep)
    lightsOn(gpioList)
    time.sleep(sleep)
    lightsOff(gpioList)


def singleLighting(gpioList, sleep):
    for gpioNum in gpioList:
        time.sleep(sleep)
        lightsOn([gpioNum])
        time.sleep(sleep)
        lightsOff([gpioNum])

def main():
    init()

    try:
        i = 0
        while i < 10:
            allLighting(LIGHT_GROUP_ALL, 2)
            singleLighting(LIGHT_GROUP_ALL, 1)
            singleLighting(LIGHT_GROUP_A, 0.1)
            singleLighting(LIGHT_GROUP_A, 0.1)
            singleLighting(LIGHT_GROUP_B, 0.1)
            singleLighting(LIGHT_GROUP_B, 0.1)
            singleLighting(LIGHT_GROUP_C, 0.1)
            singleLighting(LIGHT_GROUP_C, 0.1)
            blinkLighting([17], 0.1, 10)
            blinkLighting([27], 0.1, 10)
            blinkLighting([26], 0.1, 10)
            alternateLighting(LIGHT_GROUP_RED, 0.3, 3)
            alternateLighting(LIGHT_GROUP_GREEN, 0.3, 3)
            alternateLighting(LIGHT_GROUP_YELLOW, 0.3, 3)

            i = i + 1

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
