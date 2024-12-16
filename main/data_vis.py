"""
Liang Lu 
CS 528 - Assignment 2 
Due Date: Oct 13, 2024 
This is the file for visualizing raw data from IMU vs time. 
*** I only remove the initial datapoints because it makes it clear to see the trends. *** 
"""
import os
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt

def data_vis_multiple_signals(file_name, title, signals, labels, time):
    plt.figure(figsize=(10, 6))
    for i, signal in enumerate(signals):
        plt.plot(time, signal, label=labels[i])

    plt.title(f"{title} vs. Time for {file_name}")
    plt.xlabel("Time (s)")
    plt.ylabel(f"{title}")
    plt.grid(True)
    plt.legend()
    plt.show()

def data_vis_multiple_signals_subplots(file_name, title, signals, labels, time):
    fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    fig.suptitle(f"{title} for {file_name}", fontsize=16)
    x_min, x_max = -0.25, 4.25 

    for i, signal in enumerate(signals):
        axes[0].plot(time, signal, label=labels[i])
    axes[0].set_title("Without Removing Datapoints")
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel(title)
    axes[0].grid(True)
    axes[0].legend()
    axes[0].set_xlim(x_min, x_max)

    skip_duration = 0.85 
    num_skip = int(sampling_rate * skip_duration)
    time = time[num_skip:]
    signals = [signal[num_skip:] for signal in signals]

    for i, signal in enumerate(signals):
        axes[1].plot(time, signal, label=labels[i])
    axes[1].set_title("With Removing Initial Datapoints")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel(title)
    axes[1].grid(True)
    axes[1].legend()
    axes[1].set_xlim(x_min, x_max)

    plt.tight_layout()
    # plt.savefig(os.path.join('.', 'graph', 'vis', f"vis_{file_name}_{title.lower()[:3]}.png"))
    plt.show()

def data_vis(title, signal, time):
    plt.plot(time, signal)
    plt.title(f"{title} vs. Time")
    plt.xlabel("Time (s)")
    plt.ylabel(f"{title}")
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # motions = ["up", "down", "left", "right"]
    motions = ['cw', 'ccw']
    graph_dir = os.path.join('.', 'graph', 'vis') 
    os.makedirs(graph_dir, exist_ok=True) 

    for motion in motions:
        data_dir = os.path.join('.', 'data_new', 'rotate', motion)
        for i in range(2): 
            file_name = motion + "_" + str(i)
            file_path = os.path.join(data_dir, file_name + ".csv")
            
            sampling_rate = 100 # sampling rate = 1000/10
            
            df = pd.read_csv(file_path, delimiter=',') 
            time = df[df.columns[0]].to_numpy()
            acce_x = df['acce_x'].to_numpy() 
            acce_y = df['acce_y'].to_numpy() 
            acce_z = df['acce_z'].to_numpy() 
            gyro_x = df['gyro_x'].to_numpy() 
            gyro_y = df['gyro_y'].to_numpy() 
            gyro_z = df['gyro_z'].to_numpy() 

            data_vis_multiple_signals_subplots(
                file_name, "Acceleration (X, Y, Z)", [acce_x, acce_y, acce_z],
                ["Acceleration X", "Acceleration Y", "Acceleration Z"], time
            )
            data_vis_multiple_signals_subplots(
                file_name, "Gyroscope (X, Y, Z)", [gyro_x, gyro_y, gyro_z],
                ["Gyroscope X", "Gyroscope Y", "Gyroscope Z"], time
            )

            # data_vis_multiple_signals(file_name, "Acceleration (X, Y, Z)", [acce_x, acce_y, acce_z], 
            #                             ["Acceleration X", "Acceleration Y", "Acceleration Z"], time)

            # data_vis_multiple_signals(file_name, "Gyroscope (X, Y, Z)", [gyro_x, gyro_y, gyro_z], 
            #                             ["Gyroscope X", "Gyroscope Y", "Gyroscope Z"], time)
