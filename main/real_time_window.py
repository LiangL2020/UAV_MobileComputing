###
# - wait for a period of time for first prediction to come up 
# - suggestions: use activation window and (for example) take two seconds before and two seconds after 
###

import serial
import time
import numpy as np
import joblib 
from sklearn.preprocessing import StandardScaler
from collections import deque

SERIAL_PORT = '/dev/tty.usbserial-110'
BAUD_RATE = 115200
TRUNCATE_LENGTH = 240
GESTURES = [
    "curved_up", "curved_down", "curved_left", "curved_right",
    "straight_up", "straight_down", "straight_left", "straight_right", "none_none"
]

svm_model = joblib.load('../model/model.pkl')
# scaler = joblib.load('../model/scaler.pkl')

# sliding window for real-time gesture prediction
data_buffer = deque(maxlen=TRUNCATE_LENGTH)

def preprocess_data(buffer):
    data = np.array(buffer)
    flattened_data = data.flatten()

    expected_length = 1026
    if len(flattened_data) < expected_length:
        flattened_data = np.pad(flattened_data, (0, expected_length - len(flattened_data)))
    elif len(flattened_data) > expected_length:
        flattened_data = flattened_data[:expected_length]

    # return scaler.transform(flattened_data.reshape(1, -1))
    return flattened_data.reshape(1, -1)

def parse_line(line, line_data):
    try:
        if "time" in line:
            time_value = float(line.split("time:")[1].strip())
            line_data['timestamp'] = time_value
        elif "acce_x" in line:
            acce_values = [float(val.split(":")[1].strip()) for val in line.split("mpu6050 test: ")[1].split(",")]
            line_data.update({'acce_x': acce_values[0], 'acce_y': acce_values[1], 'acce_z': acce_values[2]})
        elif "gyro_x" in line:
            gyro_values = [float(val.split(":")[1].strip()) for val in line.split("mpu6050 test: ")[1].split(",")]
            line_data.update({'gyro_x': gyro_values[0], 'gyro_y': gyro_values[1], 'gyro_z': gyro_values[2]})
    except Exception as e:
        line_data = {} 
        print(f"Skipping malformed data: {line}, error: {e}")

    required_keys = ['timestamp', 'acce_x', 'acce_y', 'acce_z', 'gyro_x', 'gyro_y', 'gyro_z']
    return all(key in line_data for key in required_keys)

def predict_gesture(model, data):
    prediction = model.predict(data)
    return GESTURES[prediction[0]]


if __name__ == '__main__':
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        line_data = {} 

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()

                if parse_line(line, line_data):
                    data_point = [
                        line_data['acce_x'], line_data['acce_y'], line_data['acce_z'],
                        line_data['gyro_x'], line_data['gyro_y'], line_data['gyro_z']
                    ]
                    data_buffer.append(data_point)
                    line_data.clear()

                    if len(data_buffer) == TRUNCATE_LENGTH:
                        preprocessed_data = preprocess_data(data_buffer)
                        gesture = predict_gesture(svm_model, preprocessed_data)
                        data_buffer = []
                        print(f"Predicted Gesture: {gesture}")

    except KeyboardInterrupt:
        print("Exiting...")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        if ser:
            ser.close()
            print("Serial connection closed.")

