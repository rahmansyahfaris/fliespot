from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
import cflib.crtp

cflib.crtp.init_drivers()

def list_all_parameters(cf):
    # Callback function for when a parameter is found
    def param_callback(name, value):
        print(f"{name}: {value}")

    # Iterate over all parameters and use the callback to print them
    for group in cf.param.toc.toc.keys():
        for param in cf.param.toc.toc[group].keys():
            full_param_name = f"{group}.{param}"
            value = cf.param.get_value(full_param_name)
            print(f"{full_param_name}: {value}")

def main():
    uri = 'radio://0/80/2M'

    # Initialize the Crazyflie object
    cf = Crazyflie()

    # Use SyncCrazyflie for connection management
    with SyncCrazyflie(uri, cf=cf) as scf:
        # List all parameters
        list_all_parameters(cf)

if __name__ == '__main__':
    main()
