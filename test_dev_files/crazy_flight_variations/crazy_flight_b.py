import time
from datetime import datetime
import os
import math
import cflib
from cflib.crazyflie import Crazyflie
from dotenv import load_dotenv
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from multiprocessing import Process, Event
from threading import Thread
from cflib.crazyflie.log import LogConfig



# for LED blink test
def ledBlink(common_var):
    print("Starting blink")
    cflib.crtp.init_drivers()
    # Blink the LED using loop
    with SyncCrazyflie(common_var['uri']['uri'], cf=Crazyflie(rw_cache='./cache')) as scf:
        print("Connected to Crazyflie")
        time.sleep(common_var['config']['led_blink_duration'])
    print("Blink completed")
    return

def crazyFlight(common_var, common_event):

    # URI to the Crazyflie to connect to
    uri = uri_helper.uri_from_env(default=common_var['uri']['uri'])

    # The default height for takeoff
    DEFAULT_HEIGHT = common_var['config']['default_height']  # in meters

    # Initialize the low-level drivers
    #cflib.crtp.init_drivers()

    # Initialize the low-level drivers (don't list the debug drivers)
    try:
        cflib.crtp.init_drivers(enable_debug_driver=False)
    except Exception as err:
        print(f"Crazy Flight Process Terminating due to {err}")
        common_event["finishCrazyFlight"].set()
        return

    # Desired positions relative to the drone
    pos_desired_x = 0.0
    pos_desired_y = 0.0

    isEnteringNewMovement = False # trigger when entering movement to zero/reset the coordinates
    yawDegreeChange = 0 # angle to recalculate and transform logging values into relative coordinate values

    # the checkpoint that will zero/reset the coordinates
    pos_checkpoint_x = 0.0
    pos_checkpoint_y = 0.0

    start_time = time.perf_counter()

    cs_log_file_path = f"{common_var['config']['logs_directory']}log_cs_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.txt"
    cs_log_file = open(cs_log_file_path, "w")


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
        nonlocal pos_checkpoint_x, pos_checkpoint_y
        nonlocal isEnteringNewMovement, yawDegreeChange
        global pos_current_x, pos_current_y
        global pos_logging_x, pos_logging_y
        # logging (global) points (can reach 14 decimal numbers behind the point)
        pos_logging_x = data['stateEstimate.x']
        pos_logging_y = data['stateEstimate.y']
        # only for logging, does not affect flight
        yaw_logging = data['stateEstimate.yaw']
        pos_logging_z = data['stateEstimate.z']
        bat_logging = data['pm.vbat']
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
        # logging print
        """"""
        print(f"[{current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}] ET: {elapsed_time * 1000:.3f} ms "
              f"| x_cur: {round(pos_current_x,common_var['config']['logging_decimal_places'])} | y_cur: {round(pos_current_y,common_var['config']['logging_decimal_places'])} "
              f"| x_log: {round(pos_logging_x,common_var['config']['logging_decimal_places'])} | y_log: {round(pos_logging_y,common_var['config']['logging_decimal_places'])} "
              f"| z_log: {round(pos_logging_z,common_var['config']['logging_decimal_places'])} | yaw: {round(yaw_logging,common_var['config']['logging_decimal_places'])} "
              f"| bat: {round(bat_logging,common_var['config']['logging_decimal_places'])}")
        
        # logging print (comma separated)
        """"""
        cs_log_line = (
            f"{current_datetime.strftime('%Y,%m,%d,%H,%M,%S')},{elapsed_time * 1000:.3f},{round(pos_current_x, 3)},"
            f"{round(pos_current_y, 3)},{round(pos_logging_x, 3)},{round(pos_logging_y, 3)},"
            f"{round(pos_logging_z, 3)},{round(yaw_logging, 3)},{round(bat_logging, 3)}\n"
        )
        cs_log_file.write(cs_log_line)

        
        #print(f"t: {timestamp} | x_cur: {round(pos_current_x,2)} | y_cur: {round(pos_current_y,2)} | x_log: {round(pos_logging_x,2)} | y_log: {round(pos_logging_y,2)} ")

    # Connect to the Crazyflie and run the sequence
    try:
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            # Set up logging
            log_conf = LogConfig(name='Logging', period_in_ms=100)
            log_conf.add_variable('stateEstimate.x', 'float')
            log_conf.add_variable('stateEstimate.y', 'float')
            log_conf.add_variable('stateEstimate.z', 'float')
            log_conf.add_variable('stateEstimate.yaw', 'float')
            log_conf.add_variable('pm.vbat', 'float')
            
            scf.cf.log.add_config(log_conf)
            log_conf.data_received_cb.add_callback(log_pos_callback)
            print("FLIGHT STATUS: Starting log")
            log_conf.start()

            print("FLIGHT STATUS: Taking off")
            #isEnteringNewMovement = True
            with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
                print("FLIGHT STATUS: Little pause before starting")
                pos_desired_x = 0.0
                pos_desired_y = 0.0
                initial_timeout = 5 # in seconds
                initial_start_time = time.time()
                while True:
                    initial_elapsed_time = time.time() - initial_start_time
                    if common_event['crazyAbortEvent'].is_set():
                        print("FLIGHT STATUS: Aborting Flight")
                        break
                    if initial_elapsed_time > initial_timeout:
                        print("FLIGHT STATUS: Initial pause completed")
                        break
                    mc.start_linear_motion(0, 0, 0)
                    time.sleep(0.1) # little delay to not overwhelm the drone
                mc.start_linear_motion(0, 0, 0) # stay still
                #time.sleep(2)

                print("FLIGHT STATUS: Starting commanded movement")

                for index, command in enumerate(common_var['command']):
                    print(f"Command {index+1}: {command['title']}")
                    if command['x'] != 0:
                        isEnteringNewMovement = True
                        negate = 1 if command['x'] >= 0 else -1
                        yet_reached = (lambda a, b: a < b) if negate==1 else (lambda a, b: a > b)
                        pos_desired_x = command['x']
                        pos_desired_y = 0.0
                        #print("DEBUG FLIGHT: X, {command['x']} meter, ")
                        while yet_reached(pos_current_x, pos_desired_x):
                            if common_event['crazyAbortEvent'].is_set():
                                print("FLIGHT STATUS: Aborting Flight")
                                break
                            # Apply control signals
                            mc.start_linear_motion(negate*command['velocity'], 0, 0)
                            # Adding little delay to not overwhelm the drone
                            time.sleep(0.1)
                        print(f"FLIGHT STATUS: Pause before next movement ({command['hold']} seconds)")
                        mc.start_linear_motion(0, 0, 0) # stay still
                        isEnteringNewMovement = True
                        pos_desired_x = 0.0
                        pos_desired_y = 0.0
                        hold_duration = command['hold']
                        hold_time_start = time.time()
                        while True:
                            hold_time_elapsed = time.time() - hold_time_start
                            if hold_time_elapsed > hold_duration:
                                break
                            if common_event['crazyAbortEvent'].is_set():
                                print("FLIGHT STATUS: Aborting Flight")
                                break
                            mc.start_linear_motion(0, 0, 0)
                            time.sleep(0.1) # little delay to not overwhelm the drone
                        mc.start_linear_motion(0, 0, 0) # stay still
                        #time.sleep(2) # pause before next movement
                    elif command['y'] != 0:
                        isEnteringNewMovement = True
                        negate = 1 if command['y'] >= 0 else -1
                        yet_reached = (lambda a, b: a < b) if negate==1 else (lambda a, b: a > b)
                        pos_desired_x = 0.0
                        pos_desired_y = command['y']
                        while yet_reached(pos_current_y, pos_desired_y):
                            if common_event['crazyAbortEvent'].is_set():
                                print("FLIGHT STATUS: Aborting Flight")
                                break
                            # Apply control signals
                            mc.start_linear_motion(0, negate*command['velocity'], 0)
                            # Adding little delay to not overwhelm the drone
                            time.sleep(0.1)
                        print(f"FLIGHT STATUS: Pause before next movement ({command['hold']} seconds)")
                        mc.start_linear_motion(0, 0, 0) # stay still
                        isEnteringNewMovement = True
                        pos_desired_x = 0.0
                        pos_desired_y = 0.0
                        hold_duration = command['hold']
                        hold_time_start = time.time()
                        while True:
                            hold_time_elapsed = time.time() - hold_time_start
                            if hold_time_elapsed > hold_duration:
                                break
                            if common_event['crazyAbortEvent'].is_set():
                                print("FLIGHT STATUS: Aborting Flight")
                                break
                            mc.start_linear_motion(0, 0, 0)
                            time.sleep(0.1) # little delay to not overwhelm the drone
                        mc.start_linear_motion(0, 0, 0) # stay still
                        #time.sleep(2) # pause before next movement
                    elif command['yaw'] != 0:
                        isEnteringNewMovement = True
                        # yawDegreeChange change was moved to here (see test_pid_10.py if you want to know where
                        # it's located previously, this has made the flight more stable)
                        yawDegreeChange += command['yaw'] # yaw degree change (remember don't use equal, use increment)
                        if command['yaw'] >= 0:
                            mc.turn_left(command['yaw'], command['rate'])
                        elif command['yaw'] < 0:
                            mc.turn_right(command['yaw']*-1, command['rate'])
                        # yawDegreeChange was here previously
                        print(f"FLIGHT STATUS: Pause before next movement ({command['hold']} seconds)")
                        mc.start_linear_motion(0, 0, 0) # stay still
                        #isEnteringNewMovement = True
                        pos_desired_x = 0.0
                        pos_desired_y = 0.0
                        hold_duration = command['hold']
                        hold_time_start = time.time()
                        while True:
                            hold_time_elapsed = time.time() - hold_time_start
                            if hold_time_elapsed > hold_duration:
                                break
                            if common_event['crazyAbortEvent'].is_set():
                                print("FLIGHT STATUS: Aborting Flight")
                                break
                            mc.start_linear_motion(0, 0, 0)
                            time.sleep(0.1) # little delay to not overwhelm the drone
                        mc.start_linear_motion(0, 0, 0) # stay still
                        #time.sleep(2) # pause before next movement
                    else:
                        isEnteringNewMovement = True
                        print(f"FLIGHT STATUS: Pause before next movement ({command['hold']} seconds)")
                        mc.start_linear_motion(0, 0, 0) # stay still
                        #isEnteringNewMovement = True
                        pos_desired_x = 0.0
                        pos_desired_y = 0.0
                        hold_duration = command['hold']
                        hold_time_start = time.time()
                        while True:
                            hold_time_elapsed = time.time() - hold_time_start
                            if hold_time_elapsed > hold_duration:
                                break
                            if common_event['crazyAbortEvent'].is_set():
                                print("FLIGHT STATUS: Aborting Flight")
                                break
                            mc.start_linear_motion(0, 0, 0)
                            time.sleep(0.1) # little delay to not overwhelm the drone
                        mc.start_linear_motion(0, 0, 0) # stay still
                        #time.sleep(2) # pause before next movement
                    if common_event['crazyAbortEvent'].is_set():
                        print("FLIGHT STATUS: Aborting Flight")
                        break

                mc.stop()
                print("STATUS: Target reached, landing")
            
            log_conf.stop()
            cs_log_file.close()
            print("STATUS: Finished")
    except Exception as err:
        print(f"Crazy Flight Process Terminating due to {err}")
        #raise(err)
        common_event["finishCrazyFlight"].set()
        return

    if common_event["crazyAbortEvent"].is_set():
        #common_event['cameraAbortEvent'].wait()
        print("FLIGHT STATUS: Flight Aborted")

    print("Crazy Flight Process Terminating")
    common_event["finishCrazyFlight"].set()
    return


