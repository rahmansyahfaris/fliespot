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
                if command['yaw'] != 0 and (command['x'] != 0 or command['y'] != 0 or command['z'] != 0):
                    raise ValueError("yaw value can't be non zero if either of x, y, and z are non zero (you can't combine rotational and linear movements)")
            return commands
        else:
            # if commands is empty
            raise ValueError("Empty or invalid command inputs")

    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} Not found")
