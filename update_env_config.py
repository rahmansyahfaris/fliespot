import os

file_path = ".env"

def read_env_file():
    # Read the contents of the .env file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    env_vars = {}
    for line in lines:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            env_vars[key] = value
    
    return env_vars, lines

def update_env_variable(env_vars, key, new_value):
    # Update the value of a specific environment variable.
    env_vars[key] = new_value

def write_env_file(env_vars, lines):
    # Write the updated environment variables back to the .env file
    with open(file_path, 'w') as file:
        for line in lines:
            if line.strip() and not line.startswith('#'):
                key, _ = line.strip().split('=', 1)
                if key in env_vars:
                    file.write(f"{key}={env_vars[key]}\n")
                else:
                    file.write(line)
            else:
                file.write(line)

def change_env_value(key, new_value):
    # Change the value of an environment variable in the .env file
    env_vars, lines = read_env_file()
    update_env_variable(env_vars, key, new_value)
    write_env_file(env_vars, lines)
    print(f"Updated {key} to {new_value} in {file_path}")

