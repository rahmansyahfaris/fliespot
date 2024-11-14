import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
import time

# URI to the Crazyflie
URI = 'radio://0/80/2M/E7E7E7E7E7'

# Initialize the low-level drivers
cflib.crtp.init_drivers()

# in vscode:
# Ctrl + K + Ctrl + 0 to fold code
# Ctrl + K + Ctrl + J to unfold code

# just change at the log_conf and the callback

"""# Connect and log x,y,z data
with SyncCrazyflie(URI) as scf:
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
    log_conf.start()

    # Keep the script running to log data
    input('Press Enter to stop logging...')
    log_conf.stop()
"""

"""# Connect and log x,y,z,yaw data (not working good because yaw value keeps increasing/decreasing even though the drone stayed completely still)
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
"""

"""# Connect and log x,y,z data (now using deltas) (result: they (x and y) reset to zero shortly after movements because it is a relative path)
with SyncCrazyflie(URI) as scf:
    # Define log configuration for parameters
    log_conf = LogConfig(name='Position', period_in_ms=100)
    log_conf.add_variable('motion.deltaX', 'float')
    log_conf.add_variable('motion.deltaY', 'float')
    log_conf.add_variable('stateEstimate.z', 'float')

    # Callback for logging data
    def log_callback(timestamp, data, logconf):
        x = round(data['motion.deltaX'], 2)
        y = round(data['motion.deltaY'], 2)
        z = round(data['stateEstimate.z'], 2)
        print(f"Timestamp: {timestamp} ms, X: {x} m, Y: {y} m, Z: {z} m")

    # Add and start logging
    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(log_callback)
    log_conf.start()

    # Keep the script running to log data
    input('Press Enter to stop logging...')
    log_conf.stop()
"""

# Connect and log x,y,z data and put limits (like the code ends when the drone exceeds 1 meter forward) (unfinished)
with SyncCrazyflie(URI) as scf:

    logged_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}

    # Define log configuration for parameters
    log_conf = LogConfig(name='Position', period_in_ms=100)
    log_conf.add_variable('stateEstimate.x', 'float')
    log_conf.add_variable('stateEstimate.y', 'float')
    log_conf.add_variable('stateEstimate.z', 'float')

    # Callback for logging data
    def log_callback(timestamp, data, logconf):
        logged_position['x'] = round(data['stateEstimate.x'], 2)
        logged_position['y'] = round(data['stateEstimate.y'], 2)
        logged_position['z'] = round(data['stateEstimate.z'], 2)
        print(f"Timestamp: {timestamp} ms, X: {logged_position['x']} m, Y: {logged_position['y']} m, Z: {logged_position['z']} m")

    # Add and start logging
    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(log_callback)
    log_conf.start()

    while(True):
        if logged_position['x'] > 0.6:
            break
    print(logged_position)

    log_conf.stop()
""""""


"""# Connect and log x,y,z data
with SyncCrazyflie(URI) as scf:
    # Define log configuration for parameters
    log_conf = LogConfig(name='Position', period_in_ms=200)
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
    log_conf.start()

    # Keep the script running to log data
    input('Press Enter to stop logging...')
    log_conf.stop()
"""










# end