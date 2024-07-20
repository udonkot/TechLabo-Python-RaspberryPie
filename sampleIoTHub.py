import os
import random
import time
from azure.iot.device import IoTHubDeviceClient, Message
from dotenv import load_dotenv

load_dotenv()

#ここをプライマリ接続文字列の値に変える
CONNECTION_STRING = os.getenv('IOT_DEVICE_ID')

# Define the JSON message to send to IoT Hub.
TEMPERATURE = 20.0
HUMIDITY = 60
MSG_TXT = '{{"temperature": {temperature},"humidity": {humidity}}}'
RECIEVED_MESSAGE = 0

#受信時の処理
def message_handler(message):
    global RECIEVED_MESSAGE
    global COMMANDS
    RECIEVED_MESSAGE += 1
    print("")
    print("Message recieved")
    for property in vars(message).items():
        print("   {}".format(property))

    # Handling Message
    try:
        msg = message.data.decode('utf-8')
        print(msg)
    except Exception as e:
        print(e)

#送信処理
def run_telemetry_sample(client):
    print("IoT Hub device sending periodic messages")

    client.connect()

    while True:
        # Build the message with simulated telemetry values.
        temperature = TEMPERATURE + (random.random() * 15)
        humidity = HUMIDITY + (random.random() * 20)
        msg_txt_formatted = MSG_TXT.format(temperature=temperature, humidity=humidity)
        message = Message(msg_txt_formatted)

        # Add a custom application property to the message.
        # An IoT hub can filter on these properties without access to the message body.
        if temperature > 30:
            message.custom_properties["temperatureAlert"] = "true"
        else:
            message.custom_properties["temperatureAlert"] = "false"

        # Send the message.
        print("Sending message: {}".format(message))
        client.send_message(message)
        print("Message successfully sent")
        time.sleep(10)


def main():
    print("IoT Hub Quickstart #1 - Simulated device")
    print("Press Ctrl-C to exit")

    # Instantiate the client. Use the same instance of the client for the duration of
    # your application
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    # Run Sample
    try:
        #受信時の処理の登録
        client.on_message_received = message_handler
        run_telemetry_sample(client)
    except KeyboardInterrupt:
        print("IoTHubClient sample stopped by user")
    finally:
        # Upon application exit, shut down the client
        print("Shutting down IoTHubClient")
        client.shutdown()

if __name__ == '__main__':
    main()