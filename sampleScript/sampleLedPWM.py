import time

import RPi.GPIO as GPIO

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin for the LED
led_pin = 17

# Set the frequency for PWM
pwm_frequency = 100

# Set the duty cycle for PWM (0-100)
duty_cycle = 0

# Setup the GPIO pin for PWM
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, GPIO.LOW)
pwm = GPIO.PWM(led_pin, pwm_frequency)

# Start PWM with the initial duty cycle
pwm.start(duty_cycle)

try:
    while True:
        for dc in range(100, -1, -10):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)
        time.sleep(1)
        for dc in range(0, 101, 10):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)
        # # Change the duty cycle to control the brightness
        # new_duty_cycle = int(input("Enter duty cycle (0-100): "))
        # pwm.ChangeDutyCycle(new_duty_cycle)
except KeyboardInterrupt:
    pass

# Cleanup GPIO
pwm.stop()
GPIO.cleanup()