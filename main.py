import tkinter as tk
from multiprocessing import Process, Manager
import crazy_flight, crazy_camera, crazy_telegram, esp_alarm_trigger
from test_dev_files.crazy_flight_variations import crazy_flight_a, crazy_flight_b, crazy_flight_c # for control testing purposes
from threading import Thread
import register_commands

processes = [] # to list all child processes so that we can close all of them at once or do something about them
threads = [] # to list all the threads

def clear_events(events):
    for event in events:
        event.clear()

def startUpdateEnv():
    input_text = entryURI.get()
    update_uri(input_text)
    displayURIText = f"URI: {common_var['uri']['uri']}"
    displayURI.config(text=displayURIText)
    return

def update_uri(new_uri):
    common_var['uri']['uri'] = new_uri
    return

def crazyWait(common_event, common_var):
    if common_var['config']['flight_enabled']:
        common_event["finishCrazyFlight"].wait()
        if crazyFlightProcess.is_alive(): # check if the process still running
            crazyFlightProcess.terminate() # abruptly stops the process
            crazyFlightProcess.join() # cleaning up before continuing
        print("Crazy Flight Process Terminated")
        processes.remove(crazyFlightProcess) # remove the process in the processes list
    if common_var['camera']['camera_enabled']:
        common_event["finishCrazyCamera"].wait()
        if crazyCameraProcess.is_alive():
            crazyCameraProcess.terminate()
            crazyCameraProcess.join()
        print("Crazy Camera Process Terminated")
        processes.remove(crazyCameraProcess)
    if common_var['extras']['telegram_enabled']:
        common_event["finishCrazyTelegram"].wait()
        if crazyTelegramProcess.is_alive():
            crazyTelegramProcess.terminate()
            crazyTelegramProcess.join()
        print("Crazy Telegram Process Terminated")
    common_event['finishESPAlarm'].set()
    threads.remove(crazyThread)
    # flyButton.config(text="Fly",command=startCrazyFlight) # reset the button (commented because not thread-safe
    # use the code below (root.after) instead for thread safety and this should be used for all elements outside the
    # main thread like this one crazyFlightWait which is a function that will be run as a thread)
    if not common_event["shutdown"].is_set():
        root.after(0, lambda: flyButton.config(text="Fly!", command=startCrazyFlight, state="normal")) # reset the button
    return

def ESPAlarm(common_event, common_var): # thread to poll and trigger ESP32 alarm
    while True:
        if common_event['triggerESPAlarm'].is_set():
            # Run alarm trigger function
            esp_alarm_trigger.ESPAlarmTrigger(common_var['esp_info'])
            common_event['triggerESPAlarm'].clear()
        if common_event['finishESPAlarm'].is_set():
            print("Terminating ESP Alarm Thread")
            break
    threads.remove(espThread)

def startCrazyFlight():
    # basically starting the flying mechanism, polling for flight abort
    global processes, threads, crazyThread, espThread, crazyFlightProcess, crazyCameraProcess, crazyTelegramProcess

    # it is important to clear each events before starting again,
    # if not, it will only work the first time, the next one will be error
    clear_events([common_event['finishCrazyFlight'],
                  common_event['crazyAbortEvent'],
                  common_event['finishCrazyCamera'],
                  common_event['cameraAbortEvent'],
                  common_event['objectDetectedEvent'],
                  common_event['finishCrazyTelegram'],
                  common_event['triggerESPAlarm'],
                  common_event['finishESPAlarm']])
    
    # Process monitoring thread
    crazyThread = Thread(target=crazyWait, args=(common_event, common_var,))
    crazyThread.start() # start thread that polls
    threads.append(crazyThread)

    if common_var['extras']['esp_enabled']:
        espThread = Thread(target=ESPAlarm, args=(common_event, common_var,))
        espThread.start()
        threads.append(espThread)

    # Processes Making
    if common_var['config']['flight_enabled']:
        crazyFlightProcess = Process(target=crazy_flight.crazyFlight, args=(common_var, common_event,))
        crazyFlightProcess.start() # start separate process
        processes.append(crazyFlightProcess) # include the process in the processes list
    else:
        common_event['finishCrazyFlight'].set()
    if common_var['camera']['camera_enabled']:
        crazyCameraProcess = Process(target=crazy_camera.crazyCamera, args=(common_event, common_var))
        crazyCameraProcess.start()
        processes.append(crazyCameraProcess)
    if common_var['extras']['telegram_enabled']:
        crazyTelegramProcess = Process(target=crazy_telegram.crazyTelegram, args=(common_var,))
        crazyTelegramProcess.start()
        processes.append(crazyTelegramProcess)

    # change button to now function as abort/cancel
    flyButton.config(text="Stop",command=lambda: stopCrazyFlight(common_event))

    return

def stopCrazyFlight(common_event):
    flyButton.config(text="Terminating...", state="disabled") # button disabled waiting
    common_event['crazyAbortEvent'].set()
    # the event.set is to stop the crazyFlightThread (crazyFlightPolling function)
    # that contains the rest of the finishing tasks like resetting the buttons, etc
    # event is crazyAbortEvent
    return

def forceStop(common_event):
    common_event["finishCrazyFlight"].set()
    common_event["finishCrazyCamera"].set()
    common_event["finishCrazyTelegram"].set()

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
    flyButton = tk.Button(root, text="Fly!", command=startCrazyFlight)
    flyButton.pack(pady=10)

    # LED blink test button
    ledBlinkButton = tk.Button(root, text="Blink Test", command=lambda: crazy_flight.ledBlink(common_var))
    ledBlinkButton.pack(pady=10)

    forceStopButton = tk.Button(root, text="Force Stop", command=lambda: forceStop(common_event))
    forceStopButton.pack(pady=10)

    #open_config_button = tk.Button(root, text="Open Config Window", command=openConfig)
    #open_config_button.pack(pady=20)

    # Handle the close event to terminate the process
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the Tkinter event loop
    root.mainloop()

def openConfig():
    # Start a new window for config
    config_window = tk.Toplevel(root)
    config_window.title("Configuration")

    config_window.geometry("300x200")

    # make the window locked (modal locked window)
    config_window.grab_set()

    # Add widgets to the configuration window
    tk.Label(config_window, text="Setting 1:").pack(pady=5)
    entry1 = tk.Entry(config_window, width=30)
    entry1.pack(pady=5)
    
    tk.Label(config_window, text="Setting 2:").pack(pady=5)
    entry2 = tk.Entry(config_window, width=30)
    entry2.pack(pady=5)
    
    # Add a save button
    # tk.Button(config_window, text="Save Settings", command=lambda: save_settings(entry1.get(), entry2.get())).pack(pady=10)
    
    # Add a close button
    tk.Button(config_window, text="Close", command=config_window.destroy).pack(pady=10)

    # Extra closing procedure for unlocking window from modal locked mode
    config_window.protocol("WM_DELETE_WINDOW", lambda: close_config_window(config_window))

# Extra closing procedure function for unlocking window from modal locked mode
def close_config_window(window):
    # Release the modal lock and destroy the window
    window.grab_release()
    window.destroy()

# This function execute as an additional procedure before truly closing the program
def on_closing():
    global processes

    # Set abort events to signal processes to terminate gracefully
    common_event["shutdown"].set()
    common_event['crazyAbortEvent'].set()
    #time.sleep(0.5) # a little time

    # joining threads before processes, this is crucial
    for thread in threads:
        if thread.is_alive():
            thread.join()
    
    # update_env_config.change_env_value("URI", crazy_flight.tempURI)
    # # URI will not be saved for now
    
    for process in processes:
        if process.is_alive():
            process.terminate()
            process.join()

    root.destroy()
    #print("root destroyed")

if __name__ == "__main__":

    # unifying events and variables in the beginning, putting them inside a shared dictionary with manager

    manager = Manager() # shared events across processes and threads

    common_event = manager.dict()

    common_event['finishCrazyFlight'] = manager.Event() # event to indicate the end of crazyFlightProcess
    common_event['crazyAbortEvent'] = manager.Event()
    """ cameraAbortEvent is an event that breaks the crazyCamera loop into triggering finishCrazyCamera, ending 
    (terminating) the crazyCameraProcess. It can be triggered if crazyAbortEvent is triggered. The purpose is just
    to print "Camera Aborted" when the crazyCameraProcess finished, to differentiate termination due to abort and
    other terminations """
    common_event['cameraAbortEvent'] = manager.Event()
    common_event['objectDetectedEvent'] = manager.Event()
    """
    currently, the finishCrazyCamera event serves as an indication of camera trigger
    (even though the camera has not yet been installed) as well as an indication of
    crazyCameraProcess end or termination
    """
    common_event['finishCrazyCamera'] = manager.Event() # event to indicate that crazyCameraProcess has finished/returned
    common_event['finishCrazyTelegram'] = manager.Event()
    common_event['triggerESPAlarm'] = manager.Event() # event to trigger ESP32 Alarm
    common_event['finishESPAlarm'] = manager.Event() # event to stop ESP32 Alarm thread (espThread)
    common_event['shutdown'] = manager.Event() # event to indicate that close button is pressed

    common_var = manager.dict() # shared variables across processes and threads

    common_var['uri'] = register_commands.load_yaml_config('config/uri.yaml')
    displayURIText = f"URI: {common_var['uri']['uri']}"
    common_var['telegram_info'] = register_commands.load_yaml_config('config/telegram_info.yaml')
    common_var['config'] = register_commands.load_yaml_config('config/config.yaml')
    common_var['camera'] = register_commands.load_yaml_config('config/camera.yaml')
    common_var['extras'] = register_commands.load_yaml_config('config/extras.yaml')
    common_var['esp_info'] = register_commands.load_yaml_config('config/esp_info.yaml')
    common_var['keybinds'] = register_commands.load_yaml_config('config/keybinds.yaml')
    # Get the directory where the current script (or .exe) is located (not used, only used for debugging and emergency)
    # For Command Registering
    """
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    """
    # Command Registering
    common_var['command'] = register_commands.load_yaml_config('config/command.yaml')
    common_var['command'] = register_commands.register_inputs(f"{common_var['command']['command_directory']}{common_var['command']['command']}",
                                                              common_var)

    # debug print to see if data are correctly entered
    """
    for config in common_var:
        print(config)
        print(common_var[config])
        print("")
    """

    createTkinterGUI()