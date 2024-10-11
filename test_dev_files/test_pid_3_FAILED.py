import time
import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.log import LogConfig

# WARNING: This script is a failure, do not try unless you know what you're doing (tested on 10/10/2024)
# Test PID 3: for diagonal movement this time (FAILED: drone going to the right direction but too fast)

# Custom PID class
class PID:
    def __init__(self, Kp, Ki, Kd, setpoint=0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.previous_error = 0
        self.integral = 0

    def compute(self, current_value):
        error = self.setpoint - current_value
        self.integral += error
        derivative = error - self.previous_error
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.previous_error = error
        return output

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# Initialize the low-level drivers (don't list the debug drivers)
cflib.crtp.init_drivers(enable_debug_driver=False)

# Desired positions
desired_x = 1.0
desired_y = 1.0

# PID controllers for x and y axes
Kp = 0.1
Ki = 0.05
Kd = 0.01
pid_x = PID(Kp, Ki, Kd, setpoint=desired_x)
pid_y = PID(Kp, Ki, Kd, setpoint=desired_y)

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
        diagonal_velocity = 0.2 / (2 ** 0.5)  # Speed for each axis to achieve 0.2 diagonally
        while current_x < desired_x and current_y < desired_y:
            # Calculate control signals for x and y axes
            control_x = pid_x.compute(current_x)
            control_y = pid_y.compute(current_y)
            
            # Apply control signals with adjusted diagonal velocity
            mc.start_linear_motion(velocity_x_m=diagonal_velocity+control_x,
                                   velocity_y_m=diagonal_velocity+control_y,
                                   velocity_z_m=0)
            
            time.sleep(0.1)
        
        mc.stop()
    log_conf.stop()
