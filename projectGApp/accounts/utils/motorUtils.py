import time
import RPi.GPIO as GPIO

# Set the duty cycle for the servo motor
duty_cycle = 7.5
duty_cycle_min = 2.5
duty_cycle_max = 12.5

def initMotor():
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


    return pwm

# init the motor
def resetMotor():
    GPIO.cleanup(18)

# 指定した角度にモーターを動かす
def moveMotor(val):
    pwm = initMotor()
    # Change the duty cycle to rotate the servo motor
    duty_cycle = duty_cycle_min + (val / 180) * (duty_cycle_max - duty_cycle_min)
    pwm.ChangeDutyCycle(duty_cycle)  # Stop the PWM signal
    time.sleep(0.5)  # Short delay to stabilize
    pwm.ChangeDutyCycle(0)  # Stop the PWM signal
    time.sleep(0.5)  # Short delay to stabilize
    # pwm.stop()

def roundMotor(count):
    pwm = initMotor()
    print('Start the PWM')
    pwm.start(duty_cycle_min)
    time.sleep(1)

    # Change the duty cycle to rotate the servo motor
    pwm.ChangeDutyCycle(duty_cycle_max)
    time.sleep(0.5)  # Short delay to stabilize
    pwm.ChangeDutyCycle(0)  # Stop the PWM signal
    time.sleep(2)  # Wait for the rest of the time

    # pwm.ChangeDutyCycle(duty_cycle)
    # time.sleep(0.5)  # Short delay to stabilize
    # pwm.ChangeDutyCycle(0)  # Stop the PWM signal
    # time.sleep(2)  # Wait for the rest of the time

    pwm.ChangeDutyCycle(duty_cycle_min)
    time.sleep(0.5)  # Short delay to stabilize
    pwm.ChangeDutyCycle(0)  # Stop the PWM signal
    time.sleep(2)  # Wait for the rest of the time


    # for i in range(1, count):
    #     # Change the duty cycle to rotate the servo motor
    #     print('move Neutral position')
    #     pwm.ChangeDutyCycle(7.5)  # Neutral position
    #     time.sleep(5)

    #     print('move Clockwise rotation')
    #     pwm.ChangeDutyCycle(12.5)  # Clockwise rotation
    #     time.sleep(5)

    #     print('move Counter-clockwise rotation')
    #     pwm.ChangeDutyCycle(2.5)  # Counter-clockwise rotation
    #     time.sleep(5)

    # pwm.stop()

    # cycle = duty_cycle_min
    # for j in range(1, 5):
    #     # Change the duty cycle to rotate the servo motor
    #     print('move Neutral position')
    #     cycle = cycle - 1
    #     pwm.ChangeDutyCycle(cycle)
    #     time.sleep(0.5)  # Short delay to stabilize
    #     pwm.ChangeDutyCycle(0)  # Stop the PWM signal
    #     time.sleep(2)  # Wait for the rest of the time

    # cycle = duty_cycle
    # for i in range(1, 5):
    #     # Change the duty cycle to rotate the servo motor
    #     print('move Neutral position')
    #     cycle = duty_cycle + 1
    #     pwm.ChangeDutyCycle(cycle)
    #     time.sleep(0.5)  # Short delay to stabilize
    #     pwm.ChangeDutyCycle(0)  # Stop the PWM signal
    #     time.sleep(2)  # Wait for the rest of the time


    # for i in range(1, count):
    #     # Change the duty cycle to rotate the servo motor
    #     print('move Neutral position')
    #     pwm.ChangeDutyCycle(7.5)  # Neutral position
    #     time.sleep(0.5)  # Short delay to stabilize
    #     pwm.ChangeDutyCycle(0)  # Stop the PWM signal
    #     time.sleep(2)  # Wait for the rest of the time

    #     print('move Clockwise rotation')
    #     pwm.ChangeDutyCycle(9.5)  # Clockwise rotation
    #     time.sleep(0.5)  # Short delay to stabilize
    #     pwm.ChangeDutyCycle(0)  # Stop the PWM signal
    #     time.sleep(2)  # Wait for the rest of the time

    #     print('move Counter-clockwise rotation')
    #     pwm.ChangeDutyCycle(5.5)  # Counter-clockwise rotation
    #     time.sleep(0.5)  # Short delay to stabilize
    #     pwm.ChangeDutyCycle(0)  # Stop the PWM signal
    #     time.sleep(2)  # Wait for the rest of the time

    pwm.stop()

        # pwm.start(0.0)
        # pwm.ChangeDutyCycle(2.5)  # Neutral position
        # time.sleep(1)
        # pwm.ChangeDutyCycle(12.5)  # Clockwise rotation
        # time.sleep(1)
        # pwm.ChangeDutyCycle(7.5)  # Counter-clockwise rotation
        # time.sleep(1)
        # pwm.stop()
        
        # for i in range(-90, 91):
        #     # Change the duty cycle to rotate the servo motor
        #     dc = 2.5 + (12.0-2.5)/180*(i+90)
        #     pwm.ChangeDutyCycle(dc)  # Clockwise rotation
        #     time.sleep(0.5)
        #     pwm.ChangeDutyCycle(0.0) 
            
        # while True:
        #     # Change the duty cycle to rotate the servo motor
        #     pwm.ChangeDutyCycle(7.5)  # Neutral position
        #     time.sleep(1)
        #     pwm.ChangeDutyCycle(12.5)  # Clockwise rotation
        #     time.sleep(1)
        #     pwm.ChangeDutyCycle(2.5)  # Counter-clockwise rotation
        #     time.sleep(1)

