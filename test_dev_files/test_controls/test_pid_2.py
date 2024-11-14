import time
import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.log import LogConfig

# Test PID 2: using pid calculations directly

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# Initialize the low-level drivers (don't list the debug drivers)
cflib.crtp.init_drivers(enable_debug_driver=False)

# PID controller constants
Kp_y = 0.1
Ki_y = 0.05
Kd_y = 0.01

# Desired position
desired_x = 1.5
desired_y = 0.0

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

# PID controller for y-axis
pid_y = PID(Kp_y, Ki_y, Kd_y, setpoint=desired_y)

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
    print("STATUS: Starting log")
    log_conf.start()
    print("STATUS: Taking off")
    with MotionCommander(scf, default_height=1.0) as mc:
        print("STATUS: Little pause before moving")
        time.sleep(2)
        print("STATUS: Moving")
        while current_x < desired_x:
            # Calculate control signal for y-axis
            control_y = pid_y.compute(current_y)
            
            # Apply control signals
            mc.start_linear_motion(0.2, control_y, 0)

            # Adding little delay to not overwhelm the drone
            time.sleep(0.1)
        mc.stop()
        print("STATUS: Target reached, landing")
    log_conf.stop()
    print("STATUS: Finished")