import time
import os
import cflib
from cflib.crazyflie import Crazyflie
from dotenv import load_dotenv
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
import logging
from multiprocessing import Queue, Process, Event
from threading import Thread

def crazyCamera(event, abort_event, confirm_abort):

    iter = 10
    for i in range(iter):
        if abort_event.is_set():
            break
        print(f"crazyCamera: {i+1} of {iter}")
        time.sleep(1)
    
    print("Crazy Camera Process Terminating")
    if abort_event.is_set():
        print("Aborting Camera")
        confirm_abort.set()
        return
    event.set() # this will trigger crazyEvent
    return