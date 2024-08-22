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

def crazyCamera(finishCrazyCamera, crazyAbortEvent, cameraAbortEvent):

    iter = 10
    for i in range(iter):
        if crazyAbortEvent.is_set():
            break
        print(f"crazyCamera: {i+1} of {iter}")
        time.sleep(1)
    
    print("Crazy Camera Process Terminating")
    if crazyAbortEvent.is_set():
        print("Aborting Camera")
        cameraAbortEvent.set()
        return
    
    finishCrazyCamera.set()
    return