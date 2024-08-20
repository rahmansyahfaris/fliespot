import tkinter as tk
import time
from multiprocessing import Process, Queue, Event
import threading
import crazy_flight
import update_env_config
from threading import Thread
import os

processes = [] # to list all child processes so that we can close all of them at once or do something about them
displayURIText = f"URI: {crazy_flight.tempURI}"

def startUpdateEnv():
    input_text = entryURI.get()
    crazy_flight.update_tempURI(input_text)
    displayURIText = f"URI: {crazy_flight.tempURI}"
    displayURI.config(text=displayURIText)
    return

def crazyFlightPolling(event):
    event.wait()
    if crazyFlightProcess.is_alive(): # check if the process still running
        crazyFlightProcess.terminate() # abruptly stops the process
        crazyFlightProcess.join() # cleaning up before continuing
        print("Crazy Flight Process Terminated")
    processes.remove(crazyFlightProcess) # remove the process in the processes list
    flyButton.config(text="Fly",command=startCrazyFlight) # reset the button
    return

def startCrazyFlight():
    # basically starting the flying mechanism, polling for flight abort
    global processes, crazyFlightProcess, crazyFlightThread
    crazyFlightEvent = Event()
    crazyAbortEvent = Event()
    crazyFlightThread = Thread(target=crazyFlightPolling, args=(crazyFlightEvent,))
    crazyFlightProcess = Process(target=crazy_flight.crazyFlight,
                                 args=(crazy_flight.tempURI,
                                       crazy_flight.tempDEFAULT_HEIGHT,
                                       crazy_flight.tempSTEP_RANGE,
                                       crazy_flight.tempTOKEN,
                                       crazy_flight.tempBOT_USERNAME,
                                       crazy_flight.tempUSERNAME,
                                       crazyFlightEvent,
                                       crazyAbortEvent,))
    crazyFlightThread.start() # start thread that polls
    crazyFlightProcess.start() # start separate process
    processes.append(crazyFlightProcess) # include the process in the processes list
    flyButton.config(text="Stop",command=lambda: stopCrazyFlight(crazyAbortEvent)) # what to do with the button
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
    buttonURI = tk.Button(root, text="Change URI", command=startUpdateEnv)
    buttonURI.pack(pady=10)

    # Create a Label for URI widget to display the text
    displayURI = tk.Label(root, text=displayURIText, width=50, bg="lightgrey", anchor='w')
    displayURI.pack(pady=10)

    # Crazy flight button
    flyButton = tk.Button(root, text="Fly", command=startCrazyFlight)
    flyButton.pack(pady=10)

    # LED blink test button
    ledBlinkButton = tk.Button(root, text="Blink Test", command=crazy_flight.ledBlink)
    ledBlinkButton.pack(pady=10)

    # Handle the close event to terminate the process
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the Tkinter event loop
    root.mainloop()

# This function execute as an additional procedure before truly closing the program
def on_closing():
    global processes
    update_env_config.change_env_value("URI", crazy_flight.tempURI)
    for process in processes:
        if process.is_alive():
            process.terminate()
    root.destroy()

if __name__ == "__main__":
    createTkinterGUI()