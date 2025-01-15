#import os
import sys
import yaml

def extract_text(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Critical error: The file at {file_path} was not found.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
    
def register_string(command_str, common_var):
    # Default values for the command keys
    DEFAULT_VALUES = {
        'title': '',
        'x': 0.0,
        'y': 0.0,
        'z': 0.0,
        'velocity': common_var['config']['default_velocity'],
        'yaw': 0.0,
        'rate': common_var['config']['default_yaw_rate'],
        'hold': common_var['config']['default_hold_time'],
        'note': ''
    }

    # Read and parse the commands from the string
    try:
        commands = []

        # Split the string into lines
        for line in command_str.splitlines():
            # Strip whitespace and check if the line is not empty
            stripped_line = line.strip()
            if stripped_line:  # Proceed only if the line is not empty
                # Create a new copy of the default values
                command_dict = DEFAULT_VALUES.copy()
                parts = stripped_line.split(',')
                for part in parts:
                    key, value = part.split(':', 1)  # Split on the first colon
                    key = key.strip()
                    value = value.strip()
                    if key in ['x', 'y', 'z', 'velocity', 'yaw', 'rate', 'hold']:
                        # These parameters are numeric float values
                        try:
                            command_dict[key] = float(value)
                        except ValueError:
                            print(f"Invalid number for {key}: {value}")
                    else:
                        # Non-numeric values (title, note) are just strings
                        command_dict[key] = value
                commands.append(command_dict)
        
        # Check if commands is empty
        if commands:
            for command in commands:
                total_movement_input = (
                    int(bool(command['yaw'])) +
                    int(bool(command['x'])) +
                    int(bool(command['y'])) +
                    int(bool(command['z']))
                )
                movement_invalid = total_movement_input not in [0, 1]
                if movement_invalid:
                    raise ValueError(
                        f"Invalid movement input: only either yaw, x, y, or z can have a non-zero value. "
                        f"Total input given is {total_movement_input} when only 0 or 1 is allowed.\n"
                        f"Check inputs, x: {command['x']}, y: {command['y']}, z: {command['z']}, yaw: {command['yaw']}"
                    )
            return commands
        else:
            # If commands is empty
            raise ValueError("Empty or invalid command inputs")

    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")


def register_inputs(file_path, common_var):
    # Default values for the command keys
    DEFAULT_VALUES = {
        'title': '',
        'x': 0.0,
        'y': 0.0,
        'z': 0.0,
        'velocity': common_var['config']['default_velocity'],
        'yaw': 0.0,
        'rate': common_var['config']['default_yaw_rate'],
        'hold': common_var['config']['default_hold_time'],
        'note': ''
    }

    # Read and parse the commands from the text file
    try:
        commands = []

        # Read commands from the file
        with open(file_path, 'r') as file:
            for line in file:
                # Strip whitespace and check if the line is not empty
                stripped_line = line.strip()
                if stripped_line:  # Proceed only if the line is not empty
                    # .copy() method is needed in the line below, if not included, DEFAULT_VALUES will also
                    # change because of how python works (it treats value assigning by pointing to 
                    # memories, not creating a new copy, use deepcopy if the dictionary is more complex)
                    command_dict = DEFAULT_VALUES.copy()
                    parts = stripped_line.split(',')
                    for part in parts:
                        key, value = part.split(':', 1)  # Split on the first colon
                        key = key.strip()
                        value = value.strip()
                        if key in ['x', 'y', 'z', 'velocity', 'yaw', 'rate', 'hold']:
                            # these parameters are in numeric float values
                            try:
                                command_dict[key] = float(value)
                            except ValueError:
                                print(f"Invalid number for {key}: {value}")
                        else:
                            # Non-numeric values (title, note) are just strings
                            command_dict[key] = value
                    #print(f"command_dict after: {command_dict}")
                    commands.append(command_dict)
        
        # check if commands is empty
        if commands:
            #print(f"Commands: {commands}")
            for command in commands:
                total_movement_input = int(bool(command['yaw']))+int(bool(command['x']))+int(bool(command['y']))+int(bool(command['z']))
                movement_invalid = True
                if total_movement_input==1 or total_movement_input==0:
                    movement_invalid = False
                if movement_invalid:
                    raise ValueError(f"Invalid movement input: only either yaw, x, y, or z can have non-zero value, total input given is {total_movement_input} when only 0 or 1 is allowed\n"
                                     f"Check inputs, x: {command['x']}, y: {command['y']}, z: {command['z']}, yaw: {command['yaw']}")
            return commands
        else:
            # if commands is empty
            raise ValueError("Empty or invalid command inputs")

    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} Not found")
    
def load_yaml_config(file_path):
    """Load a YAML configuration file. If loading fails, raise an exception to stop the program."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Critical error: '{file_path}' not found. Exiting.")
        sys.exit(1)  # Exits the program with an error code
    except yaml.YAMLError as e:
        print(f"Critical error parsing '{file_path}': {e}. Exiting.")
        sys.exit(1)  # Exits the program with an error code