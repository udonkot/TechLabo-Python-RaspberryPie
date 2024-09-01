import time

import RPi.GPIO as GPIO

# Set the GPIO mode
print('Set the GPIO mode')
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin for the servo motor
servo_pin = 18

# Set the frequency for PWM
frequency = 50

# Set the duty cycle for the servo motor
duty_cycle = 7.5

# Configure the GPIO pin as PWM output
print('Configure the GPIO pin as PWM output')
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, frequency)

# Start the PWM with the initial duty cycle
print('Start the PWM')
pwm.start(duty_cycle)

def main():
    try:



        while True:
            # pwm.ChangeDutyCycle(7.5)  # Neutral position
            # print('Slowly move loop')
            # for angle in range(0, 180, 1):
            #     duty_cycle = angle / 18 + 2.5
            #     pwm.ChangeDutyCycle(duty_cycle)
            #     time.sleep(0.3) 
            # time.sleep(5)

            # for angle in range(1, 3, 1):
            #     pwm.ChangeDutyCycle(angle * 2.5)  # Neutral position
            #     time.sleep(1)

            # for angle in range(3, 1, -1):
            #     pwm.ChangeDutyCycle(angle * 2.5)  # Neutral position
            #     time.sleep(1)



            # # Change the duty cycle to rotate the servo motor
            print('move 7.5')
            pwm.ChangeDutyCycle(7.5)  # Neutral position
            time.sleep(2)
            print('move 10.5')
            pwm.ChangeDutyCycle(10.5)  # Clockwise rotation
            time.sleep(2)
            # # print('move 7.5')
            # pwm.ChangeDutyCycle(7.5)  # Neutral position
            # time.sleep(2)
            print('move 5')
            pwm.ChangeDutyCycle(5)  # Neutral position
            time.sleep(2)
            # # print('move 2.5')
            # pwm.ChangeDutyCycle(2.5)  # Counter-clockwise rotation
            # time.sleep(2)
            # # print('move 5')
            # pwm.ChangeDutyCycle(5)  # Neutral position
            # time.sleep(1)

    except KeyboardInterrupt:
        # Stop the PWM and cleanup the GPIO
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
