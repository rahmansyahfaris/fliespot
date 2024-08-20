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
                event,
                abort_event):

    crazyCameraEvent = Event()
    cameraAbortEvent = Event()
    crazyCameraProcess = Process(target=crazy_camera.crazyCamera, args=(crazyCameraEvent, abort_event, cameraAbortEvent,))
    crazyTelegramProcess = Process(target=crazy_telegram.crazyTelegram, args=(token, bot_username, username))
    crazyCameraProcess.start()
    crazyTelegramProcess.start()

    iter = 20
    for i in range(iter):
        if abort_event.is_set(): # checks for crazyAbortEvent
            print("Aborting Flight")
            break
        if crazyCameraEvent.is_set(): # checks for crazyCameraEvent
            print("Crazy Camera Trigger")
            break
        print(f"crazyFlight: {i+1} of {iter}")
        time.sleep(1)

    if abort_event.is_set():
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
    event.set()
    return


