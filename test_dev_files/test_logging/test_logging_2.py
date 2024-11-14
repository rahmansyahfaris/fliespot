import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
import time

# URI to the Crazyflie
URI = 'radio://0/80/2M/E7E7E7E7E7'

# Initialize the low-level drivers
cflib.crtp.init_drivers()


# Connect and log x,y,z,yaw data (not working good because yaw value keeps increasing/decreasing even though the drone stayed completely still)
with SyncCrazyflie(URI) as scf:
    # Define log configuration for parameters
    log_conf = LogConfig(name='Position', period_in_ms=100)
    log_conf.add_variable('stateEstimate.x', 'float')
    log_conf.add_variable('stateEstimate.y', 'float')
    log_conf.add_variable('stateEstimate.z', 'float')
    log_conf.add_variable('stateEstimate.yaw', 'float')

    # Callback for logging data
    def log_callback(timestamp, data, logconf):
        x = round(data['stateEstimate.x'], 2)
        y = round(data['stateEstimate.y'], 2)
        z = round(data['stateEstimate.z'], 2)
        yaw = round(data['stateEstimate.yaw'], 2)
        print(f"Timestamp: {timestamp} ms, X: {x} m, Y: {y} m, Z: {z} m, yaw: {yaw} degree")

    # Add and start logging
    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(log_callback)
    log_conf.start()

    # Keep the script running to log data
    input('Press Enter to stop logging...')
    log_conf.stop()