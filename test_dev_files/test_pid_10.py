import time
from datetime import datetime
import math
import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.log import LogConfig

# Test PID 10:
# - rotations with the mathematical formulas now to allow all kinds of angles

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# The default height for takeoff
DEFAULT_HEIGHT = 1  # in meters

# Initialize the low-level drivers
cflib.crtp.init_drivers()

# Initialize the low-level drivers (don't list the debug drivers)
cflib.crtp.init_drivers(enable_debug_driver=False)

# PID controller constants
Kp_y = 0.1
Ki_y = 0.05
Kd_y = 0.01
# PID controller constants
Kp_x = 0.1
Ki_x = 0.05
Kd_x = 0.01

# Desired positions relative to the drone
pos_desired_x = 0.0
pos_desired_y = 0.0

isEnteringNewMovement = False # trigger when entering movement to zero/reset the coordinates
yawDegreeChange = 0 # angle to recalculate and transform logging values into relative coordinate values

# the checkpoint that will zero/reset the coordinates
pos_checkpoint_x = 0.0
pos_checkpoint_y = 0.0

start_time = time.perf_counter()

# PID controller class
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

# function to help transform global logging points to relative points (relative to the drone each movement)
def cf_relative(xlog, ylog, xche, yche, degree):
    degree_360 = degree % 360   
    radians = math.radians(degree_360)
    def yaw_transformation(request, x, y):
        if request == 'x':
            return (x * math.cos(-radians)) - (y * math.sin(-radians))
        elif request == 'y':
            return (x * math.sin(-radians)) + (y * math.cos(-radians))
        else:
            raise ValueError(f"Invalid requested new axis point: {request}, please choose either 'x' or 'y'.")
    xlogmche = yaw_transformation('x', xlog, ylog) - yaw_transformation('x', xche, yche)
    ylogmche = yaw_transformation('y', xlog, ylog) - yaw_transformation('y', xche, yche)
    relative_result_dict = {'x': xlogmche, 'y': ylogmche}
    return relative_result_dict

# logging loop function
def log_pos_callback(timestamp, data, logconf):
    global pos_current_x, pos_current_y, pos_checkpoint_x, pos_checkpoint_y
    global pos_logging_x, pos_logging_y, isEnteringNewMovement, yawDegreeChange
    # logging (global) points (can reach 14 decimal numbers behind the point)
    pos_logging_x = data['stateEstimate.x']
    pos_logging_y = data['stateEstimate.y']
    # only for logging, does not affect flight
    yaw_logging = data['stateEstimate.yaw']
    pos_logging_z = data['stateEstimate.z'] 
    # entering new movement will adjust the checkpoint to zero the coordinates relative to the current drone's position
    if isEnteringNewMovement:
        pos_checkpoint_x = pos_logging_x
        pos_checkpoint_y = pos_logging_y
        isEnteringNewMovement = False
    # bundle / pack of positions to be recalculated and transformed into relative points in the cf_relative function
    pos_pack = pos_logging_x, pos_logging_y, pos_checkpoint_x, pos_checkpoint_y, yawDegreeChange
    # current (relative) points
    pos_current_x = cf_relative(*pos_pack)['x']
    pos_current_y = cf_relative(*pos_pack)['y']
    # time and date stuff
    current_datetime = datetime.now()
    elapsed_time = time.perf_counter() - start_time
    print(f"[{current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}] ET: {elapsed_time * 1000:.3f} ms | x_cur: {round(pos_current_x,2)} | y_cur: {round(pos_current_y,2)} | x_log: {round(pos_logging_x,2)} | y_log: {round(pos_logging_y,2)} | z_log: {round(pos_logging_z,2)} | yaw: {round(yaw_logging,2)}")
    #print(f"t: {timestamp} | x_cur: {round(pos_current_x,2)} | y_cur: {round(pos_current_y,2)} | x_log: {round(pos_logging_x,2)} | y_log: {round(pos_logging_y,2)} ")

# Connect to the Crazyflie and run the sequence
with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
    # Set up logging
    log_conf = LogConfig(name='Position', period_in_ms=100)
    log_conf.add_variable('stateEstimate.x', 'float')
    log_conf.add_variable('stateEstimate.y', 'float')
    log_conf.add_variable('stateEstimate.z', 'float')
    log_conf.add_variable('stateEstimate.yaw', 'float')
    
    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(log_pos_callback)
    print("STATUS: Starting log")
    log_conf.start()

    print("STATUS: Taking off")
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        print("STATUS: Little pause before starting")
        pos_desired_x = 0.0
        pos_desired_y = 0.0
        pid_x = PID(Kp_x, Ki_x, Kd_x, setpoint=pos_desired_x)
        pid_y = PID(Kp_y, Ki_y, Kd_y, setpoint=pos_desired_y)
        initial_timeout = 5 # in seconds
        initial_start_time = time.time()
        while True:
            initial_elapsed_time = time.time() - initial_start_time
            if initial_elapsed_time > initial_timeout:
                print("STATUS: Initial pause completed")
                break
            control_velocity_x = pid_x.compute(pos_current_x)
            control_velocity_y = pid_y.compute(pos_current_y)
            mc.start_linear_motion(control_velocity_x, control_velocity_y, 0)
            time.sleep(0.1) # little delay to not overwhelm the drone
        mc.start_linear_motion(0, 0, 0) # stay still
        #time.sleep(2)

        print("STATUS: Turning")
        isEnteringNewMovement = True
        mc.turn_left(45)
        yawDegreeChange += 45 # yaw degree change (remember don't use equal, use increment)
        print("STATUS: Pause before next movement")
        mc.start_linear_motion(0, 0, 0) # stay still
        #isEnteringNewMovement = True
        pos_desired_x = 0.0
        pos_desired_y = 0.0
        pid_x = PID(Kp_x, Ki_x, Kd_x, setpoint=pos_desired_x)
        pid_y = PID(Kp_y, Ki_y, Kd_y, setpoint=pos_desired_y)
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
        #time.sleep(2) # pause before next movement

        print("STATUS: Movement 1")
        isEnteringNewMovement = True
        pos_desired_x = 1.0
        pos_desired_y = 0.0
        pid_y = PID(Kp_y, Ki_y, Kd_y, setpoint=pos_desired_y)
        while pos_current_x < pos_desired_x:
            # Calculate control signal for y-axis
            control_velocity_y = pid_y.compute(pos_current_y)
            # Apply control signals
            mc.start_linear_motion(0.2, control_velocity_y, 0)
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
        #time.sleep(2) # pause before next movement

        mc.stop()
        print("STATUS: Target reached, landing")
    
    log_conf.stop()
    print("STATUS: Finished")