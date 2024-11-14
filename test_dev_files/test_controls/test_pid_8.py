import time
from datetime import datetime
import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.log import LogConfig

# Test PID 8:
# - now moving in y axis

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# The default height for takeoff
DEFAULT_HEIGHT = 1  # in meters

# Initialize the low-level drivers
cflib.crtp.init_drivers()

# Initialize the low-level drivers (don't list the debug drivers)
#cflib.crtp.init_drivers(enable_debug_driver=False)

# PID controller constants
Kp_y = 0.1
Ki_y = 0.05
Kd_y = 0.01
# PID controller constants
Kp_x = 0.1
Ki_x = 0.05
Kd_x = 0.01

# Desired position (now will be updated along the way, that's why it is commented)
pos_desired_x = 0.0
pos_desired_y = 0.0

isEnteringNewMovement = False # trigger when entering movement to zero/reset the coordinates

# the checkpoint that will zero/reset the coordinates
pos_checkpoint_x = 0.0
pos_checkpoint_y = 0.0

start_time = time.perf_counter()

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

# PID controller for y-axis (now will be updated along the way, that's why it is commented)
# pid_y = PID(Kp_y, Ki_y, Kd_y, setpoint=pos_desired_y)

def log_pos_callback(timestamp, data, logconf):
    global pos_current_x, pos_current_y, pos_checkpoint_x, pos_checkpoint_y, pos_logging_x, pos_logging_y, isEnteringNewMovement
    pos_logging_x = data['stateEstimate.x']
    pos_logging_y = data['stateEstimate.y']
    if isEnteringNewMovement:
        pos_checkpoint_x = pos_logging_x
        pos_checkpoint_y = pos_logging_y
        isEnteringNewMovement = False
    pos_current_x = pos_logging_x - pos_checkpoint_x
    pos_current_y = pos_logging_y - pos_checkpoint_y
    current_datetime = datetime.now()
    elapsed_time = time.perf_counter() - start_time
    print(f"[{current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}] ET: {elapsed_time * 1000:.3f} ms | x_cur: {round(pos_current_x,2)} | y_cur: {round(pos_current_y,2)} | x_log: {round(pos_logging_x,2)} | y_log: {round(pos_logging_y,2)}")
    #print(f"t: {timestamp} | x_cur: {round(pos_current_x,2)} | y_cur: {round(pos_current_y,2)} | x_log: {round(pos_logging_x,2)} | y_log: {round(pos_logging_y,2)} ")

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
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        print("STATUS: Little pause before starting")
        mc.start_linear_motion(0, 0, 0) # initial zeroing movements
        pos_desired_x = 0.0
        pos_desired_y = 0.0
        pid_x = PID(Kp_x, Ki_x, Kd_x, setpoint=pos_desired_x)
        pid_y = PID(Kp_y, Ki_y, Kd_y, setpoint=pos_desired_y)
        initial_timeout = 5 # in seconds
        initial_start_time = time.time()
        while True:
            initial_elapsed_time = time.time() - initial_start_time
            if initial_elapsed_time > initial_timeout:
                print("STATUS: Little pause completed")
                break
            control_velocity_x = pid_x.compute(pos_current_x)
            control_velocity_y = pid_y.compute(pos_current_y)
            mc.start_linear_motion(control_velocity_x, control_velocity_y, 0)
            time.sleep(0.1) # little delay to not overwhelm the drone
        mc.start_linear_motion(0, 0, 0) # stay still
        #time.sleep(2)

        print("STATUS: Movement 1")
        isEnteringNewMovement = True
        pos_desired_x = 0.0
        pos_desired_y = 1.0
        pid_x = PID(Kp_x, Ki_x, Kd_x, setpoint=pos_desired_x)
        while pos_current_y < pos_desired_y:
            # Calculate control signal for x-axis
            control_velocity_x = pid_x.compute(pos_current_x)
            # Apply control signals
            mc.start_linear_motion(control_velocity_x, 0.2, 0)
            # Adding little delay to not overwhelm the drone
            time.sleep(0.1)
        print("STATUS: Pause before next movement")
        mc.start_linear_motion(0, 0, 0) # stay still
        isEnteringNewMovement = True
        pos_desired_x = 0.0
        pos_desired_y = 0.0
        hold_duration = 2
        hold_time_start = time.time()
        while True:
            hold_time_elapsed = time.time() - hold_time_start
            if hold_time_elapsed > hold_duration:
                break
            control_velocity_x = pid_x.compute(pos_current_x)
            control_velocity_y = pid_y.compute(pos_current_y)
            mc.start_linear_motion(control_velocity_x, control_velocity_y, 0)
            time.sleep(0.1) # little delay to not overwhelm the drone
        mc.start_linear_motion(0, 0, 0) # stay still

        print("STATUS: Movement 2")
        isEnteringNewMovement = True
        pos_desired_x = 0.0
        pos_desired_y = -1.0
        pid_x = PID(Kp_x, Ki_x, Kd_x, setpoint=pos_desired_x)
        while pos_current_y > pos_desired_y:
            # Calculate control signal for x-axis
            control_velocity_x = pid_x.compute(pos_current_x)
            # Apply control signals
            mc.start_linear_motion(control_velocity_x, -0.2, 0)
            # Adding little delay to not overwhelm the drone
            time.sleep(0.1)
        print("STATUS: Pause before next movement")
        mc.start_linear_motion(0, 0, 0) # stay still
        isEnteringNewMovement = True
        pos_desired_x = 0.0
        pos_desired_y = 0.0
        hold_duration = 2
        hold_time_start = time.time()
        while True:
            hold_time_elapsed = time.time() - hold_time_start
            if hold_time_elapsed > hold_duration:
                break
            control_velocity_x = pid_x.compute(pos_current_x)
            control_velocity_y = pid_y.compute(pos_current_y)
            mc.start_linear_motion(control_velocity_x, control_velocity_y, 0)
            time.sleep(0.1) # little delay to not overwhelm the drone
        mc.start_linear_motion(0, 0, 0) # stay still

        mc.stop()
        print("STATUS: Target reached, landing")
    
    log_conf.stop()
    print("STATUS: Finished")