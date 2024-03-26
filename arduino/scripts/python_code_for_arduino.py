import serial.tools.list_ports
from flask import Flask, request, jsonify
import threading
from through_socket_produce_Data import send_message_to_server

app = Flask(__name__)


def main(portVar):
    serialInst = serial.Serial(port=portVar, baudrate=9600)

    # Function to continuously read sensor data
    def read_sensor_data():
        while True:
            # Read sensor data from Arduino
            sensor_data = serialInst.readline().decode('utf-8').strip()
           # print("Sensor data:", sensor_data)
            send_message_to_server(sensor_data)

    # Start a new thread to read sensor data
    sensor_thread = threading.Thread(target=read_sensor_data)
    # Set the thread as daemon so it will exit when the main program exits
    sensor_thread.daemon = True
    sensor_thread.start()

    @app.route("/on", methods=["POST"])
    def turn_on():
        command = "ON"
        send_command_to_arduino(command)
        return jsonify({"message": "LED turned ON"})

    @app.route("/off", methods=["POST"])
    def turn_off():
        command = "OFF"
        send_command_to_arduino(command)
        return jsonify({"message": "LED turned OFF"})

    def send_command_to_arduino(command):
        # Sending command to Arduino
        serialInst.write(command.encode('utf-8'))

    if __name__ == "__main__":
        app.run()


if __name__ == "__main__":
    ports = serial.tools.list_ports.comports()
    portsList = []

    for onePort in ports:
        portsList.append(str(onePort))
        print(str(onePort))

    val = input("Select Port: COM")
    portVar = "COM" + str(val)
    print(portVar)

    main(portVar)