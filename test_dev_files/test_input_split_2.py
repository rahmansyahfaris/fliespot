import os
import sys

# Test Input Split 2: where only either yaw, x, or y that can have non zero value (unfinished)

def register_inputs(file_path):
    # Default values for the command keys
    DEFAULT_VALUES = {
        'title': '',
        'x': 0.0,
        'y': 0.0,
        'z': 0.0,
        'velocity': 0.2,
        'yaw': 0.0,
        'rate': 30,
        'hold': 1.0,
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
                    command_dict = DEFAULT_VALUES
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
                    commands.append(command_dict)
        
        # check if commands is empty
        if commands:
            for command in commands:
                total_movement_input = int(bool(command['yaw']))+int(bool(command['x']))+int(bool(command['y']))+int(bool(command['z']))
                movement_invalid = True
                if total_movement_input==1 or total_movement_input==0:
                    movement_invalid = False
                if movement_invalid:
                    raise ValueError(f"Invalid movement input: only either yaw, x, y, or z can have non-zero value, total input given is {total_movement_input} when only 0 or 1 is allowed")
            return commands
        else:
            # if commands is empty
            raise ValueError("Empty or invalid command inputs")

    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} Not found")

# Get the directory where the current script (or .exe) is located
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the commands.txt file
file_path = os.path.join(script_dir, 'test_inputs/test_input_1.txt')

print(register_inputs(file_path=file_path))