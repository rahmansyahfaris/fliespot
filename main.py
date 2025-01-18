import tkinter as tk
from multiprocessing import Process, Manager, Event
from flask import Flask, jsonify, request, render_template
import logging
import crazy_flight, crazy_camera, esp_alarm_trigger
#from test_dev_files.crazy_flight_variations import crazy_flight_a, crazy_flight_b, crazy_flight_c # for control testing purposes
from threading import Thread
import register_commands

processes = [] # to list all child processes so that we can close all of them at once or do something about them
threads = [] # to list all the threads

app = Flask(__name__, template_folder="webapp/templates", static_folder="webapp/static") # flask app server

# Flask Routes Functions:
# Default configuration values

@app.route("/")
def index():
    return render_template("index.html", configurations=common_var)

@app.route('/set_configs', methods=['POST'])
def set_configs():

    # Update configurations and perform necessary actions
    common_var['config']['default_height'] = float(request.form.get('default_height'))
    common_var['config']['default_velocity'] = float(request.form.get('default_velocity'))
    common_var['config']['default_hold_time'] = float(request.form.get('default_hold_time'))
    common_var['config']['flight_enabled'] = bool(request.form.get('flight_enabled'))
    common_var['camera']['camera_enabled'] = bool(request.form.get('camera_enabled'))
    common_var['extras']['esp_enabled'] = bool(request.form.get('esp_enabled'))
    common_var['config']['default_yaw_rate'] = float(request.form.get('default_yaw_rate'))
    common_var['config']['initial_pause_duration'] = float(request.form.get('initial_pause_duration'))
    common_var['camera']['detection_classes'] = request.form.get('detection_classes')
    common_var['camera']['confidence_threshold'] = float(request.form.get('confidence_threshold'))
    common_var['camera']['flight_on_found_stay_duration'] = float(request.form.get('flight_on_found_stay_duration'))
    common_var['command'] = request.form.get('command').replace('\r\n', '\n')

    print(request.form.to_dict)
    #print(common_var)

    # Return a success message
    return jsonify({"message": "Configurations updated successfully!"})

@app.route('/crazy_start', methods=['GET'])
def web_crazy_start():
    if common_event['ready'].is_set() and not common_event['error'].is_set():
        common_event['ready'].clear()
        startCrazyFlight()
        return jsonify({"status": "Started"})
    else:
        return jsonify({"status": "Not started (not ready or busy)"})
    
@app.route('/crazy_stop', methods=['GET'])
def web_crazy_stop():
    if not common_event['crazyAbortEvent'].is_set():
        stopCrazyFlight(common_event)
        return jsonify({"status": "Stopped"})
    else:
        return jsonify({"status": "Not stopped (busy)"})

@app.route('/crazy_check', methods=['GET'])
def crazy_check():
    return jsonify({"ready":  common_event['ready'].is_set(),
                    "error_occurred": common_event['error'].is_set(),
                    "aborted": common_event['crazyAbortEvent'].is_set(),
                    "detected": common_event['objectDetectedEvent'].is_set()})

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
    common_event['finishESPAlarm'].set()
    # it is important to clear each events before starting again,
    # if not, it will only work the first time, the next one will be error
    clear_events([common_event['finishCrazyFlight'],
                  common_event['crazyAbortEvent'],
                  common_event['finishCrazyCamera'],
                  common_event['cameraAbortEvent'],
                  common_event['objectDetectedEvent'],
                  common_event['triggerESPAlarm'],
                  common_event['finishESPAlarm'],
                  common_event['error']])
    
    common_var['command'] = common_var['command_temp'] # returning commands into text format
    threads.remove(crazyThread)
    
    if common_var['extras']['tkinter_instead']:
        # flyButton.config(text="Fly",command=startCrazyFlight) # reset the button (commented because not thread-safe
        # use the code below (root.after) instead for thread safety and this should be used for all elements outside the
        # main thread like this one crazyFlightWait which is a function that will be run as a thread)
        if not common_event["shutdown"].is_set():
            root.after(0, lambda: flyButton.config(text="Fly!", command=startCrazyFlight, state="normal")) # reset the button
    
    common_event['ready'].set()
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
    global processes, threads, crazyThread, espThread, crazyFlightProcess, crazyCameraProcess

    if not common_var['extras']['tkinter_instead']:
        common_var['command_temp'] = common_var['command']
        common_var['command'] = register_commands.register_string(command_str=common_var['command'],
                                                                  common_var=common_var)
    #print(common_var)
    
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
        crazyCameraProcess = Process(target=crazy_camera.crazyCamera, args=(common_event, common_var,))
        crazyCameraProcess.start()
        processes.append(crazyCameraProcess)

    # change button to now function as abort/cancel
    if common_var['extras']['tkinter_instead']:
        flyButton.config(text="Stop",command=lambda: stopCrazyFlight(common_event))

    return

def stopCrazyFlight(common_event):
    if common_var['extras']['tkinter_instead']:
        flyButton.config(text="Terminating...", state="disabled") # button disabled waiting
    common_event['crazyAbortEvent'].set()
    # the event.set is to stop the crazyFlightThread (crazyFlightPolling function)
    # that contains the rest of the finishing tasks like resetting the buttons, etc
    # event is crazyAbortEvent
    return

def forceStop(common_event):
    common_event["finishCrazyFlight"].set()
    common_event["finishCrazyCamera"].set()
    
# Tkinter GUI function:
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

    # Handle the close event to terminate the process
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the Tkinter event loop
    root.mainloop()

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
    
    for process in processes:
        if process.is_alive():
            process.terminate()
            process.join()

    root.destroy()
    #print("root destroyed")

if __name__ == "__main__":

    # unifying events and variables in the beginning, putting them inside a shared dictionary with manager

    manager = Manager() # for shared variables and events across processes and threads

    common_event = manager.dict() # dictionary for shared events across processes and threads

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
    common_event['triggerESPAlarm'] = manager.Event() # event to trigger ESP32 Alarm
    common_event['finishESPAlarm'] = manager.Event() # event to stop ESP32 Alarm thread (espThread)
    common_event['ready'] = manager.Event() # event that indicates ready to operate
    #common_event['busy'] = manager.Event() # event that indicates the program is busy and shouldn't get any updates
    common_event['error'] = manager.Event() # event that indicates that error occured
    common_event['shutdown'] = manager.Event() # event to indicate that close button is pressed

    common_var = manager.dict() # dictionary for shared variables across processes and threads

    # the manager.dict() is also required here for the nested dictionaries too, otherwise only the first dimension can
    # have the interprocess communication, the nested dict will stay the same if you don't do this
    common_var['uri'] = manager.dict(register_commands.load_yaml_config('config/uri.yaml'))
    displayURIText = f"URI: {common_var['uri']['uri']}"
    common_var['config'] = manager.dict(register_commands.load_yaml_config('config/config.yaml'))
    common_var['camera'] = manager.dict(register_commands.load_yaml_config('config/camera.yaml'))
    common_var['extras'] = manager.dict(register_commands.load_yaml_config('config/extras.yaml'))
    common_var['esp_info'] = manager.dict(register_commands.load_yaml_config('config/esp_info.yaml'))
    common_var['keybinds'] = manager.dict(register_commands.load_yaml_config('config/keybinds.yaml'))
    # Get the directory where the current script (or .exe) is located (not used, only used for debugging and emergency)
    # For Command Registering
    """
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    """
    # Command Registering
    common_var['command'] = manager.dict(register_commands.load_yaml_config('config/command.yaml'))
    common_var['command_temp'] = None

    # debug print to see if data are correctly entered
    """
    for config in common_var:
        print(config)
        print(common_var[config])
        print("")
    """
    if common_var['extras']['tkinter_instead']:
        common_var['command'] = register_commands.register_inputs(f"{common_var['command']['command_directory']}{common_var['command']['command']}", common_var)
        createTkinterGUI()
    else:
        common_var['command'] = register_commands.extract_text(f"{common_var['command']['command_directory']}{common_var['command']['command']}")
        logging.basicConfig(filename='flask.log', level=logging.INFO)
        common_event['ready'].set()
        #print("LOG ESTABLISHED")
        #print(common_var)
        app.run(debug=True, host='0.0.0.0', port=8080) # don't use debug (unless it is in the main block, you will encounter pickle error) and 
        # use host 0.0.0.0 instead of 127.0.0.1 to enable all interfaces (so you can access through your phones, etc) but it makes it vulnerable