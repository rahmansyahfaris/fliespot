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

"""
currently, the finishCrazyCamera event serves as an indication of camera trigger
(even though the camera has not yet been installed) as well as an indication of
crazyCameraProcess end or termination
"""

# Load the environment variables
load_dotenv()

URI = os.getenv("URI") # example URI = radio://0/80/2M/E7E7E7E7E7
tempURI = URI # temporary URI, will be updated using save or save & exit
DEFAULT_HEIGHT = os.getenv("DEFAULT_HEIGHT") # in meters
tempDEFAULT_HEIGHT = DEFAULT_HEIGHT
LED_BLINK_DURATION = int(os.getenv("LED_BLINK_DURATION")) # in seconds
tempLED_BLINK_DURATION = LED_BLINK_DURATION
STEP_RANGE = float(os.getenv("STEP_RANGE"))
tempSTEP_RANGE = STEP_RANGE
TOKEN = os.getenv("TOKEN")
tempTOKEN = TOKEN
BOT_USERNAME = os.getenv("BOT_USERNAME")
tempBOT_USERNAME = BOT_USERNAME
USERNAME = os.getenv("USERNAME")
tempUSERNAME = USERNAME

cflib.crtp.init_drivers()

def update_tempURI(new_value):
    global tempURI
    tempURI = new_value
    return

# for LED blink test
def ledBlink():
    print("Starting blink")
    # Blink the LED using loop
    with SyncCrazyflie(tempURI, cf=Crazyflie(rw_cache='./cache')) as scf:
        print("Connected to Crazyflie")
        time.sleep(LED_BLINK_DURATION)
    print("Blink completed")
    return

def crazyFlight(uri,
                default_height,
                step_range,
                token,
                bot_username,
                username,
                finishCrazyFlight,
                crazyAbortEvent):

    finishCrazyCamera = Event() # event to indicate that crazyCameraProcess has finished/returned
    """ cameraAbortEvent is an event that breaks the crazyCamera loop into triggering finishCrazyCamera, ending 
    (terminating) the crazyCameraProcess. It can be triggered if crazyAbortEvent is triggered. The purpose is just
    to print "Camera Aborted" when the crazyCameraProcess finished, to differentiate termination due to abort and
    other terminations """
    cameraAbortEvent = Event()
    crazyCameraProcess = Process(target=crazy_camera.crazyCamera, args=(finishCrazyCamera, crazyAbortEvent, cameraAbortEvent,))
    crazyTelegramProcess = Process(target=crazy_telegram.crazyTelegram, args=(token, bot_username, username))
    crazyCameraProcess.start()
    crazyTelegramProcess.start()

    iter = 20
    for i in range(iter):
        if crazyAbortEvent.is_set(): # checks for crazyAbortEvent
            print("Aborting Flight")
            break
        if finishCrazyCamera.is_set(): # checks for finishCrazyCamera
            print("Crazy Camera Trigger")
            break
        print(f"crazyFlight: {i+1} of {iter}")
        time.sleep(1)

    if crazyAbortEvent.is_set():
        cameraAbortEvent.wait()
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
    finishCrazyFlight.set()
    return


