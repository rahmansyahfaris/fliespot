import tkinter as tk
import time
from multiprocessing import Process, Queue, Event, Manager
import threading
import crazy_flight
import update_env_config
from threading import Thread
import os
import yaml

# configuration
# usage: variable_name['key'] to get the value
# ex: uri['uri'] will get the value of uri in uri.yaml
# ex: config['default_height'] will get the value of default_height in config.yaml
# "config" is used not because the file name is config.yaml but because the
# variable assigned to yaml.safe_load (the one with equal sign) in the with statement is called config
with open('config/uri.yaml','r') as file:
    uri = yaml.safe_load(file)
    # the default and example URI is radio://0/80/2M/E7E7E7E7E7
with open('config/telegram_info.yaml','r') as file:
    telegram_info = yaml.safe_load(file)
with open('config/config.yaml','r') as file:
    config = yaml.safe_load(file)


processes = [] # to list all child processes so that we can close all of them at once or do something about them
displayURIText = f"URI: {uri['uri']}"

def startUpdateEnv():
    input_text = entryURI.get()
    update_uri(input_text)
    displayURIText = f"URI: {uri['uri']}"
    displayURI.config(text=displayURIText)
    return

def update_uri(new_uri):
    uri['uri'] = new_uri
    return

def crazyFlightWait(event):
    event.wait()
    if crazyFlightProcess.is_alive(): # check if the process still running
        crazyFlightProcess.terminate() # abruptly stops the process
    # crazyFlightProcess.join() # cleaning up before continuing
    print("Crazy Flight Process Terminated")
    processes.remove(crazyFlightProcess) # remove the process in the processes list
    flyButton.config(text="Fly",command=startCrazyFlight) # reset the button
    return

def startCrazyFlight():
    # basically starting the flying mechanism, polling for flight abort
    global processes, crazyFlightProcess, crazyFlightThread

    # it is important to clear each events before starting again,
    # if not, it will only work the first time, the next one will be error
    common_event['finishCrazyFlight'].clear()
    common_event['crazyAbortEvent'].clear()
    common_event['finishCrazyCamera'].clear()
    common_event['cameraAbortEvent'].clear()

    crazyFlightThread = Thread(target=crazyFlightWait, args=(common_event["finishCrazyFlight"],))
    crazyFlightProcess = Process(target=crazy_flight.crazyFlight, args=(uri, telegram_info, config, common_event,))
    crazyFlightThread.start() # start thread that polls
    crazyFlightProcess.start() # start separate process
    processes.append(crazyFlightProcess) # include the process in the processes list
    # change button to now function as abort/cancel
    flyButton.config(text="Stop",command=lambda: stopCrazyFlight(common_event["crazyAbortEvent"]))
    return

def stopCrazyFlight(event):
    flyButton.config(text="Terminating...") # button disabled waiting
    event.set()
    # the event.set is to stop the crazyFlightThread (crazyFlightPolling function)
    # that contains the rest of the finishing tasks like resetting the buttons, etc
    # event is crazyAbortEvent
    return

def createTkinterGUI():
    global root, flyButton, displayURI, entryURI

    # Create the main application window
    root = tk.Tk()
    root.title("Fliespot")

    # Create an Entry for URI widget
    entryURI = tk.Entry(root, width=50)
    entryURI.pack(pady=10)

    # Create a Button for URI widget
    buttonURI = tk.Button(root, text="Change URI")
    buttonURI.pack(pady=10)

    # Create a Label for URI widget to display the text
    displayURI = tk.Label(root, text=displayURIText, width=50, bg="lightgrey", anchor='w')
    displayURI.pack(pady=10)

    # Crazy flight button
    flyButton = tk.Button(root, text="Fly", command=startCrazyFlight)
    flyButton.pack(pady=10)

    # LED blink test button
    ledBlinkButton = tk.Button(root, text="Blink Test", command=lambda: crazy_flight.ledBlink(uri, config))
    ledBlinkButton.pack(pady=10)

    # Handle the close event to terminate the process
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the Tkinter event loop
    root.mainloop()

# This function execute as an additional procedure before truly closing the program
def on_closing():
    global processes
    # update_env_config.change_env_value("URI", crazy_flight.tempURI)
    # # URI will not be saved for now
    for process in processes:
        if process.is_alive():
            process.terminate()
        process.join()
    root.destroy()

if __name__ == "__main__":

    # unifying events in the beginning, putting them inside a shared dictionary with manager

    manager = Manager()

    common_event = manager.dict()

    common_event['finishCrazyFlight'] = manager.Event()
    common_event['crazyAbortEvent'] = manager.Event()
    """ cameraAbortEvent is an event that breaks the crazyCamera loop into triggering finishCrazyCamera, ending 
    (terminating) the crazyCameraProcess. It can be triggered if crazyAbortEvent is triggered. The purpose is just
    to print "Camera Aborted" when the crazyCameraProcess finished, to differentiate termination due to abort and
    other terminations """
    common_event['cameraAbortEvent'] = manager.Event()
    """
    currently, the finishCrazyCamera event serves as an indication of camera trigger
    (even though the camera has not yet been installed) as well as an indication of
    crazyCameraProcess end or termination
    """
    common_event['finishCrazyCamera'] = manager.Event() # event to indicate that crazyCameraProcess has finished/returned

    createTkinterGUI()