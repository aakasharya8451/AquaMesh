import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import json
from flask import Flask, jsonify
import random
import time
from kafka.producer import produce_messages

app = Flask(__name__)


class LEDController:
    def __init__(self):
        self.led_state = False

    def update_led(self):
        if self.led_state:
            print("Green LED ON")
            print("Red LED OFF")
        else:
            print("Green LED OFF")
            print("Red LED ON")

    def set_led_status(self, value):
        if value == '1':
            self.led_state = True
        else:
            self.led_state = False
        self.update_led()


led_controller = LEDController()


def get_moisture_data(arduino_id, lower_limit, upper_limit):
    time.sleep(1)
    moisture = random.randint(lower_limit, upper_limit)
    data = {
        "arduinoID": arduino_id,
        "moisture": moisture
    }
    json_data = json.dumps(data)
    return json_data


def simulate_moisture_sensor_arduino(arduino_id, lower_limit, upper_limit):
    while True:
        json_data = get_moisture_data(arduino_id, lower_limit, upper_limit)
        # print(json_data)
        partition_no = json.loads(json_data)["arduinoID"]
        produce_messages(json_data, partition_no)
        


@app.route('/on', methods=['POST'])
def turn_led_on():
    print("Turning LED on")
    led_controller.set_led_status('1')
    return jsonify({"message": "LED turned ON"})


@app.route('/off', methods=['POST'])
def turn_led_off():
    print("Turning LED off")
    led_controller.set_led_status('0')
    return jsonify({"message": "LED turned OFF"})


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python simulator.py <arduino_id> <lower_limit> <upper_limit> <port>")
        sys.exit(1)

    arduino_id = int(sys.argv[1])
    lower_limit = int(sys.argv[2])
    upper_limit = int(sys.argv[3])
    port = int(sys.argv[4])

    simulator = threading.Thread(target=simulate_moisture_sensor_arduino, args=(
        arduino_id, lower_limit, upper_limit))
    # Set the thread as daemon so it will exit when the main thread exits
    simulator.daemon = True
    simulator.start()
    app.run(debug=True, port=port)  # Start the Flask web server
