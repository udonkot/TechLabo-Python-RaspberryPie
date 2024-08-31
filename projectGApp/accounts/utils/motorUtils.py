import time

import RPi.GPIO as GPIO

# Set the GPIO mode
print('Set the GPIO mode')
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin for the servo motor
servo_pin = 17

# Set the frequency and duty cycle for the servo motor
frequency = 50

# Set the duty cycle for the servo motor
duty_cycle = 7.5
duty_cycle_min = 2.5
duty_cycle_max = 12.5

# Initialize the GPIO pin for the servo motor
print('Initialize the GPIO pin for the servo motor')
GPIO.setup(servo_pin, GPIO.OUT)

# Create a PWM object for the servo motor
pwm = GPIO.PWM(servo_pin, frequency)

# Function to set the angle of the servo motor
# def set_angle(angle):
#     duty_cycle = duty_cycle_min + (angle / 180) * (duty_cycle_max - duty_cycle_min)
#     pwm.start(duty_cycle)
#     time.sleep(1)
#     pwm.stop()

# # Example usage
# set_angle(90)  # Set the servo motor to 90 degrees

# # Clean up the GPIO
# GPIO.cleanup()

# 
def roundMotor(count):
    print('Start the PWM')
    pwm.start(duty_cycle)
    
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

    for i in range(1, 12):
        # Change the duty cycle to rotate the servo motor
        print('move Neutral position')
        cycle = i + 0.5
        pwm.ChangeDutyCycle(cycle)
        # time.sleep(0.5)  # Short delay to stabilize
        # pwm.ChangeDutyCycle(0)  # Stop the PWM signal
        # time.sleep(2)  # Wait for the rest of the time

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

    pwm.stop(duty_cycle)

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

