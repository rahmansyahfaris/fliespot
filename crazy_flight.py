import time
import os
import cflib
from cflib.crazyflie import Crazyflie
from dotenv import load_dotenv
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from multiprocessing import Process, Event
from threading import Thread
import logging
import process_functions
import crazy_camera
import crazy_telegram

# Load the environment variables
load_dotenv()

cflib.crtp.init_drivers()

# update_tempURI function now placed in main.py

# for LED blink test
def ledBlink(common_var):
    print("Starting blink")
    # Blink the LED using loop
    with SyncCrazyflie(common_var['uri']['uri'], cf=Crazyflie(rw_cache='./cache')) as scf:
        print("Connected to Crazyflie")
        time.sleep(common_var['config']['led_blink_duration'])
    print("Blink completed")
    return

def crazyFlight(common_var, common_event):
    crazyCameraProcess = Process(target=crazy_camera.crazyCamera, args=(common_event,))
    crazyTelegramProcess = Process(target=crazy_telegram.crazyTelegram, args=(common_var,))
    crazyCameraProcess.start()
    crazyTelegramProcess.start()

    # this iterations and loops simulate camera activity
    iter = 20
    for i in range(iter):
        if common_event["crazyAbortEvent"].is_set(): # checks for crazyAbortEvent
            print("Aborting Flight")
            break
        if common_event['finishCrazyCamera'].is_set(): # checks for finishCrazyCamera
            print("Crazy Camera Trigger")
            break
        print(f"crazyFlight: {i+1} of {iter} (URI: {common_var['uri']['uri']})")
        time.sleep(1)

    if common_event["crazyAbortEvent"].is_set():
        common_event['cameraAbortEvent'].wait()
        print("Camera Aborted")

    # making sure crazyCameraProcess is finished clean
    if crazyCameraProcess.is_alive():
        crazyCameraProcess.terminate()
        crazyCameraProcess.join()
        print("Crazy Camera Process Terminated")

    if crazyTelegramProcess.is_alive():
        crazyTelegramProcess.terminate()
        crazyTelegramProcess.join()
        print("Crazy Telegram Process Terminated")

    print("Crazy Flight Process Terminating")
    common_event["finishCrazyFlight"].set()
    return


