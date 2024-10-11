import cflib.crtp
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

# URI to the Crazyflie
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# Initialize the low-level drivers
cflib.crtp.init_drivers()

# Connect and log data
with SyncCrazyflie(URI) as scf:
    # Define log configuration for battery voltage
    log_conf = LogConfig(name='Battery', period_in_ms=1000)
    log_conf.add_variable('pm.vbat', 'float')

    # Callback for logging data
    def log_callback(timestamp, data, logconf):
        print(f"Timestamp: {timestamp} ms, Battery voltage: {round(data['pm.vbat'], 2)} V")

    # Add and start logging
    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(log_callback)
    log_conf.start()

    # Keep the script running to log data
    input('Press Enter to stop logging...')
    log_conf.stop()
