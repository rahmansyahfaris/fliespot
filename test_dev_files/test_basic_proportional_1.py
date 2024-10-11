import time
import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.log import LogConfig

# Basic Proportional Control 1

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# Initialize the low-level drivers (don't list the debug drivers)
cflib.crtp.init_drivers(enable_debug_driver=False)

# Proportional control constants
Kp_x = 0.1
Kp_y = 0.1

# Desired position
desired_x = 1.0
desired_y = 0.0

def log_pos_callback(timestamp, data, logconf):
    global current_x, current_y
    current_x = data['stateEstimate.x']
    current_y = data['stateEstimate.y']
    print(f"t: {timestamp} | x: {round(current_x,2)} | y: {round(current_y,2)}")

# Connect to the Crazyflie and run the sequence
with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
    # Set up logging
    log_conf = LogConfig(name='Position', period_in_ms=100)
    log_conf.add_variable('stateEstimate.x', 'float')
    log_conf.add_variable('stateEstimate.y', 'float')
    
    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(log_pos_callback)
    log_conf.start()
    
    with MotionCommander(scf, default_height=1.0) as mc:
        print("STATUS: Take off")
        while True:
            # Calculate errors
            error_x = desired_x - current_x
            error_y = desired_y - current_y
            
            # Calculate control signals
            control_x = Kp_x * error_x
            control_y = Kp_y * error_y
            
            # Apply control signals
            mc.start_linear_motion(control_x, control_y, 0)
            
            # Check if the Crazyflie has reached the desired position
            if abs(error_x) < 0.05 and abs(error_y) < 0.05:  # Tolerance of 5 cm
                break
            
            # Small delay to prevent overwhelming the Crazyflie
            time.sleep(0.1)
        
        print("STATUS: Stopping")
        mc.stop()
    log_conf.stop()
    print("STATUS: Flight stopped")
