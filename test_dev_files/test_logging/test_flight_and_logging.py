import time
import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig



# URI to your Crazyflie
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# The default height for takeoff
DEFAULT_HEIGHT = 1  # in meters

# Initialize the low-level drivers
cflib.crtp.init_drivers()

# in vscode:
# Ctrl + K + Ctrl + 0 to fold code
# Ctrl + K + Ctrl + J to unfold code

"""# Simple flight with logging
if __name__ == '__main__':
    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        # Define log configuration for parameters
        log_conf = LogConfig(name='Position', period_in_ms=100)
        log_conf.add_variable('stateEstimate.x', 'float')
        log_conf.add_variable('stateEstimate.y', 'float')
        log_conf.add_variable('stateEstimate.z', 'float')

        # Callback for logging data
        def log_callback(timestamp, data, logconf):
            x = round(data['stateEstimate.x'], 2)
            y = round(data['stateEstimate.y'], 2)
            z = round(data['stateEstimate.z'], 2)
            print(f"Timestamp: {timestamp} ms, X: {x} m, Y: {y} m, Z: {z} m")

        # Add and start logging
        scf.cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(log_callback)
        print("log started")
        log_conf.start()
        print("flight starting")

        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            time.sleep(1)
            print("here we go")
            mc.forward(1)
            time.sleep(1)
            print("Before landing")
            log_conf.stop()

        print("flight ended")
"""

# Self correcting initial position (unfinished)
if __name__ == '__main__':
    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        # Define log configuration for parameters
        log_conf = LogConfig(name='Position', period_in_ms=100)
        log_conf.add_variable('stateEstimate.x', 'float')
        log_conf.add_variable('stateEstimate.y', 'float')
        log_conf.add_variable('stateEstimate.z', 'float')

        # Callback for logging data
        def log_callback(timestamp, data, logconf):
            x = round(data['stateEstimate.x'], 2)
            y = round(data['stateEstimate.y'], 2)
            z = round(data['stateEstimate.z'], 2)
            print(f"Timestamp: {timestamp} ms, X: {x} m, Y: {y} m, Z: {z} m")

        # Add and start logging
        scf.cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(log_callback)
        print("log started")
        log_conf.start()
        print("flight starting")

        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            time.sleep(1)
            print("here we go")
            mc.forward(1)
            time.sleep(1)
            print("Before landing")
            log_conf.stop()

        print("flight ended")
""""""