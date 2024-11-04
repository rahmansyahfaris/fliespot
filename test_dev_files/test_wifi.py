import subprocess

def connect_to_wifi(ssid):
    # Command to connect to a Wi-Fi network
    command = f'netsh wlan connect name="{ssid}"'
    
    # Run the command
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Connected to {ssid}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect to {ssid}: {e}")

def disconnect_wifi():
    command = 'netsh wlan disconnect'
    
    try:
        subprocess.run(command, shell=True, check=True)
        print("Disconnected from Wi-Fi")
    except subprocess.CalledProcessError as e:
        print(f"Failed to disconnect: {e}")


# Example usage
wifi_ssid = "your_ssid" # wifi name
wifi_password = ""  # Actually not needed for this method, assumes the profile exists
command = "connect"

if command == "connect":
    connect_to_wifi(wifi_ssid, wifi_password)
elif command == "disconnect":
    disconnect_wifi()
