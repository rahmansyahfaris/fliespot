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

def crazyWait(queue: Queue):
    while(True):
        # queue is common_event_queue
        # queue_data is the data (status) we get from common_event_queue, which is the dictionary with 2 keys or more
        # first key is feature which is what part of process or feature does it relate (flight, camera, or anything else)
        # second key is state which is what is the state of the feature now that is given
        # there may be other keys to add more details, descriptions, or contexts
        # unfortunately, this is all failed attempt
        queue_data = queue.get()
        if (queue_data['feature'] == 'crazy_flight'):
            if (queue_data['state'] == 'is_returned'):
                if crazyFlightProcess.is_alive(): # check if the process still running
                    crazyFlightProcess.terminate() # abruptly stops the process
                # crazyFlightProcess.join() # cleaning up before continuing
                print("Crazy Flight Process Terminated")
                processes.remove(crazyFlightProcess) # remove the process in the processes list
                flyButton.config(text="Fly",command=startCrazyFlight) # reset the button
                break
        # elif (queue_data['feature'] == 'crazy_camera') 
    return

def startCrazyFlight():
    # basically starting the flying mechanism, polling for flight abort
    global processes, crazyFlightProcess, crazyFlightThread

    crazyFlightThread = Thread(target=crazyWait, args=(common_event_queue,))
    crazyFlightProcess = Process(target=crazy_flight.crazyFlight, args=(uri, telegram_info, config, common_event_queue,))
    crazyFlightThread.start() # start thread that polls
    crazyFlightProcess.start() # start separate process
    processes.append(crazyFlightProcess) # include the process in the processes list
    # change button to now function as abort/cancel
    flyButton.config(text="Stop",command=lambda: stopCrazyFlight(common_event_queue))
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

    # now we are using queue to signal events with flexibility
    # it will contain a dictionary, at least with 2 keys, may have more for added details and contexts
    # go to the function crazyWait for more details about this queue mechanism,
    # it is a function that will poll incoming data of the queue and act according the data given
    common_event_queue = Queue()

    createTkinterGUI()