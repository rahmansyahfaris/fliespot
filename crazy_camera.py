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

def crazyCamera(common_event):

    # this iterations and loops simulate camera activity
    iter = 10
    for i in range(iter):
        if common_event['crazyAbortEvent'].is_set():
            break
        print(f"crazyCamera: {i+1} of {iter}")
        time.sleep(1)
    
    print("Crazy Camera Process Terminating")
    if common_event['crazyAbortEvent'].is_set():
        print("Aborting Camera")
        common_event['cameraAbortEvent'].set()
        return
    
    common_event['finishCrazyCamera'].set()
    return