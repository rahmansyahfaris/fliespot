import requests

def ESPAlarmTrigger(param):
    # Construct the full URL
    url = f"{param['ip']}{param['endpoint']}?password={param['password']}"
    try:
        # Send the GET request to the ESP32
        response = requests.get(url)
        
        # Print the response from the ESP32
        print(f"Status Code: {response.status_code}, Response Text: {response.text}")
    except requests.ConnectionError:
        print("Failed to connect to the ESP32.")
