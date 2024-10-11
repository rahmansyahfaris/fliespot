import logging
import time
import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper



# URI to your Crazyflie
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# The default height for takeoff
DEFAULT_HEIGHT = 1  # in meters

# Initialize the low-level drivers
cflib.crtp.init_drivers()

# in vscode:
# Ctrl + K + Ctrl + 0 to fold code
# Ctrl + K + Ctrl + J to unfold code

"""# 0.1 meter letter L
# Main function
if __name__ == '__main__':
    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            # Take off and hover at the default height
            # mc.take_off()
            
            # Wait a bit
            time.sleep(3) # in seconds

            # letter L move
            mc.forward(0.1)
            time.sleep(2)
            mc.left(0.1)
            time.sleep(2)
            mc.right(0.1)
            time.sleep(2)
            mc.back(0.1)
            time.sleep(2)

            # Spin degrees
            mc.turn_left(angle_degrees=360, rate=72.0) # rate is how much degree the drone spin per second

            # pause a bit before landing again
            time.sleep(3)
            
            # Land after the spin
            # mc.land()
"""

"""# wait 2 seconds, go forward, wait 2 seconds, land
# Main function
if __name__ == '__main__':
    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            # Take off and hover at the default height
            # mc.take_off()
            
            # Wait a bit
            time.sleep(2) # in seconds

            mc.forward(0.1)

            time.sleep(2)
"""

"""# go 1 meter but in an incremental loop of 0.1 meter each and with a timer that stops the drone when the time is up (unfinished)
# Main function
if __name__ == '__main__':
    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            # Take off and hover at the default height
            # mc.take_off()
            
            # Wait a bit
            time.sleep(2) # in seconds

            mc.forward(0.1)

            time.sleep(2)
"""

# test

"""# forward 1 meter immediately
if __name__ == '__main__':
    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            time.sleep(1)
            mc.forward(2)
            time.sleep(1)
"""

"""# start linear motion test
if __name__ == '__main__':
    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            time.sleep(1)
            time.sleep(2)
            mc.stop()
            print("Stop SUCCESS")
"""

"""# start linear motion test
if __name__ == '__main__':
    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            time.sleep(1)
            mc.start_linear_motion(0.2, 0, 0)
            time.sleep(3)
            mc.stop()
"""

"""# start linear motion test, non-stop, stopped by pressing ENTER
if __name__ == '__main__':
    # SyncCrazyflie context manager to ensure connection is closed automatically
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # MotionCommander context manager for easy command of motion
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            time.sleep(2)
            mc.start_linear_motion(0.2, 0, 0)
            input("Press Enter to stop the drone...")
            mc.stop()
"""






# end