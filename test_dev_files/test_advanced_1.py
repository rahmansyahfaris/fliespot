import time
import cflib
import os
import sys
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig
import register_commands

"""
This is an advanced test flight script 1
using move_distance from motion commander
"""

# URI to your Crazyflie
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# The default height for takeoff
DEFAULT_HEIGHT = 1  # in meters

# Initialize the low-level drivers
cflib.crtp.init_drivers()

# in vscode:
# Ctrl + K + Ctrl + 0 to fold code
# Ctrl + K + Ctrl + J to unfold code

# Simple flight with logging
if __name__ == '__main__':

    # Get the directory where the current script (or .exe) is located
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    # Path to the commands.txt file
    txt_command_path = os.path.join(script_dir, 'test_dev_files/test_inputs/test_input_1.txt')

    # load the commands from the txt file
    commands = register_commands.register_inputs(txt_command_path)

    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        # Define log configuration for parameters
        log_conf = LogConfig(name='Position', period_in_ms=100)
        log_conf.add_variable('stateEstimate.x', 'float')
        log_conf.add_variable('stateEstimate.y', 'float')
        log_conf.add_variable('stateEstimate.z', 'float')
        log_conf.add_variable('pm.vbat', 'float')

        # Callback for logging data
        def log_callback(timestamp, data, logconf):
            x = round(data['stateEstimate.x'], 2)
            y = round(data['stateEstimate.y'], 2)
            z = round(data['stateEstimate.z'], 2)
            vbat = round(data['pm.vbat'], 2)
            print(f"t: {timestamp} ms | px:{x} | py:{y} | pz:{z} | bat:{vbat}")

        # Add and start logging
        scf.cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(log_callback)
        print("log started")
        log_conf.start()
        print("flight starting")

        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            print("1 sec!")
            time.sleep(1)
            print("here we go")
            for command in commands:
                mc.move_distance(distance_x_m=command['x'],
                                 distance_y_m=command['y'],
                                 distance_z_m=0,
                                 velocity=command['velocity'])
                time.sleep(command['hold'])
            print("Before landing")

        log_conf.stop()
        print("flight ended")
""""""