import time

import RPi.GPIO as GPIO

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin for the LED
# led_pins = [17]
led_pins = [20,21,6,13,19,26,16,25,12,23,24,17,27,22]

# Set the frequency for PWM
pwm_frequency = 100

# Set the duty cycle for PWM (0-100)
duty_cycle = 0

# 各ピンのPWMオブジェクトを格納するリスト
pwms = []

# 各ピンを初期化
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    pwm = GPIO.PWM(pin, pwm_frequency)
    pwm.start(0)  # 初期のデューティサイクルを0に設定
    pwms.append(pwm)


try:
    while True:
        for dc in range(100, -1, -10):
            for pwm in pwms:
                pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)
        time.sleep(1)
        for dc in range(0, 101, 10):
            for pwm in pwms:
                pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)
except KeyboardInterrupt:
    pass

# Cleanup GPIO
finally:
    for pwm in pwms:
        pwm.stop()
    GPIO.cleanup()
