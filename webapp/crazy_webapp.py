from flask import Flask, jsonify, request, render_template
from multiprocessing import Event
import logging

def webAppServerz(common_event, common_var):
    for i in range(50):
        print(f"hello {i}")



def webAppServer(common_event, common_var):

    app = Flask(__name__)
    # Shared event
    buttonChange = Event()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/crazy_start', methods=['POST'])
    def crazy_start():
        common_event["startFromWebApp"].set()  # Set the event
        return jsonify({"message": "Started from web app", "button_text": "ABORT", "next_action": "/crazy_abort", "header_text": "Operating"})

    @app.route('/crazy_abort', methods=['POST'])
    def crazy_abort():
        common_event["crazyAbortEvent"].set()  # Clear the event
        if common_event["objectDetectedEvent"].is_set():
            return jsonify({"message": "Completed from web app", "button_text": "STOP", "next_action": "", "header_text": "Completing"})
        else:
            return jsonify({"message": "Aborted from web app", "button_text": "ABORT", "next_action": ""})

    @app.route('/status', methods=['GET'])
    def check_button_status():
        if common_event["objectDetectedEvent"].is_set():
            return jsonify({"button_text": "STOP", "next_action": "/crazy_abort", "header_text": "Mission Accomplished"})
        elif common_event["startFromWebApp"].is_set():
            return jsonify({"button_text": "ABORT", "next_action": "/crazy_abort"})

    logging.basicConfig(filename='flask.log', level=logging.INFO)
    #print("LOG ESTABLISHED")
    app.run(host='0.0.0.0', port=8080) # don't use debug (you will encounter pickle error) and 
    # use host 0.0.0.0 instead of 127.0.0.1 to enable all interfaces (so you can access through your phones, etc) but it makes it vulnerable