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

    start_time = time.perf_counter()

    cs_log_file_path = f"{common_var['config']['logs_directory']}log_cs_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.txt"
    cs_log_file = open(cs_log_file_path, "w")

    # logging loop function
    def log_pos_callback(timestamp, data, logconf):
        global pos_logging_x, pos_logging_y
        # logging (global) points (can reach 14 decimal numbers behind the point)
        pos_logging_x = data['stateEstimate.x']
        pos_logging_y = data['stateEstimate.y']
        # only for logging, does not affect flight
        yaw_logging = data['stateEstimate.yaw']
        pos_logging_z = data['stateEstimate.z']
        bat_logging = data['pm.vbat']
        # time and date stuff
        current_datetime = datetime.now()
        elapsed_time = time.perf_counter() - start_time
        # logging print
        """"""
        print(f"[{current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}] ET: {elapsed_time * 1000:.3f} ms "
              f"| x_log: {round(pos_logging_x,common_var['config']['logging_decimal_places'])} | y_log: {round(pos_logging_y,common_var['config']['logging_decimal_places'])} "
              f"| z_log: {round(pos_logging_z,common_var['config']['logging_decimal_places'])} | yaw: {round(yaw_logging,common_var['config']['logging_decimal_places'])} "
              f"| bat: {round(bat_logging,common_var['config']['logging_decimal_places'])}")
        
        # logging print (comma separated)
        """"""
        cs_log_line = (
            f"{current_datetime.strftime('%Y,%m,%d,%H,%M,%S')},{elapsed_time * 1000:.3f},"
            f"{round(pos_logging_x, 3)},{round(pos_logging_y, 3)},"
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
                time.sleep(5) # in seconds

                print("FLIGHT STATUS: Starting commanded movement")

                for index, command in enumerate(common_var['command']):
                    print(f"Command {index+1}: {command['title']}")
                    if command['x'] != 0:
                        mc.move_distance(command['x'], 0, 0, command['velocity'])
                        print(f"FLIGHT STATUS: Pause before next movement ({command['hold']} seconds)")
                        time.sleep(command['hold'])
                    elif command['y'] != 0:
                        mc.move_distance(0, command['y'], 0, command['velocity'])
                        print(f"FLIGHT STATUS: Pause before next movement ({command['hold']} seconds)")
                        time.sleep(command['hold'])
                    elif command['yaw'] != 0:
                        if command['yaw'] >= 0:
                            mc.turn_left(command['yaw'], command['rate'])
                        elif command['yaw'] < 0:
                            mc.turn_right(command['yaw']*-1, command['rate'])
                        print(f"FLIGHT STATUS: Pause before next movement ({command['hold']} seconds)")
                        time.sleep(command['hold'])
                    else:
                        print(f"FLIGHT STATUS: Pause before next movement ({command['hold']} seconds)")
                        time.sleep(command['hold'])
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


