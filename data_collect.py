import serial
import serial.tools.list_ports
import os
import csv
import time

def get_port():
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in ports:
        print(f"Port: {port}, Description: {desc}, Hardware ID: {hwid}")

def open_serial_port(port='/dev/cu.usbserial-110', baudrate=115200):
    try:
        return serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        return None

def parse_line(line, line_data, start_time):
    """Parse the line and update line_data dictionary with the new data."""
    try:
        if "time" in line:
            time_stamp = time.time() - start_time
            line_data['timestamp'] = round(time_stamp, 3)
        elif "acce_x" in line:
            acce_data = line.split("mpu6050 test: ")[1]
            acce_x, acce_y, acce_z = [float(val.split(":")[1]) for val in acce_data.split(",")]
            line_data.update({'acce_x': acce_x, 'acce_y': acce_y, 'acce_z': acce_z})
        elif "gyro_x" in line:
            gyro_data = line.split("mpu6050 test: ")[1]
            gyro_x, gyro_y, gyro_z = [float(val.split(":")[1]) for val in gyro_data.split(",")]
            line_data.update({'gyro_x': gyro_x, 'gyro_y': gyro_y, 'gyro_z': gyro_z})
    except Exception as e:
        print(f"Error parsing line: {line}, error: {e}")

    required_keys = ['timestamp', 'acce_x', 'acce_y', 'acce_z', 'gyro_x', 'gyro_y', 'gyro_z']
    return all(key in line_data for key in required_keys)

def collect_gesture_data(ser, gesture_name, num_in_series, duration=5):
    """Collect data for a specific gesture and save to a CSV file."""
    data_dir = os.path.join('.', 'data', gesture_name)
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, f"{gesture_name}_{num_in_series}.csv")
    print(f"Collecting data for '{gesture_name}_{num_in_series}' gesture, saving to {file_path}")

    try:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['timestamp', 'acce_x', 'acce_y', 'acce_z', 'gyro_x', 'gyro_y', 'gyro_z'])
            writer.writeheader()
            line_data = {} 
            start_time = time.time()

            while time.time() - start_time <= duration:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    print(line)
                    
                    if parse_line(line, line_data, start_time):
                        writer.writerow(line_data)
                        line_data.clear() 

        print(f"Data collection for '{gesture_name}' completed and saved.")

    except Exception as e:
        print(f"Error during data collection for '{gesture_name}': {e}")

def main():
    ser = open_serial_port()
    if ser is None:
        print("Could not open serial port. Exiting...")
        return

    gestures = ["up", "down", "left", "right"]
    duration = 4
    num_collect = 21

    try: 
        for gesture in gestures:
            for i in range(num_collect):
                input(f"Press Enter to start collecting data for '{gesture}_{i}' gesture...")
                collect_gesture_data(ser, gesture, num_in_series=i, duration=duration)

    except KeyboardInterrupt:
        print("Data collection interrupted by user.")
    finally:
        ser.close()
        print("Serial connection closed.")

if __name__ == '__main__':
    get_port()  
    main()
