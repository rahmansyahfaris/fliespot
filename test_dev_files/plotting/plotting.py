
"""
The column names:
year,month,date,hour,minute,second,et,x_cur,y_cur,x_log,y_log,z_log,yaw,bat

Put the csv txt file in the data folder of this directory

commands to get results:
cd ./test_dev_files/plotting
python ./plotting.py
"""

import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import os

# Specify the directory containing the file
directory = './data'  # Change this to your directory path

# Get the first file in the directory
files = os.listdir(directory)
if not files:
    raise FileNotFoundError("The directory is empty. Please add a file.")
file_path = os.path.join(directory, files[0])  # Get the first file

# Define the column names
column_names = "year,month,date,hour,minute,second,et,x_cur,y_cur,x_log,y_log,z_log,yaw,bat"

# Add column names to the file if they are missing
with open(file_path, 'r+') as file:
    lines = file.readlines()
    if not lines[0].strip() == column_names:
        # Prepend the column names
        lines.insert(0, column_names + '\n')
        file.seek(0)  # Move to the beginning of the file
        file.writelines(lines)

# Load the data into a DataFrame
data = pd.read_csv(file_path)

# Extract the relevant columns
x_log = data['x_log']
y_log = data['y_log']
z_log = data['z_log']
bat = data['bat']
et = data['et']

# Define viewing range for all axes
x_range = (-1,1.5)  # Adjust as needed
y_range = (-1,1.5)  # Adjust as needed
z_range = (0,2.5)  # Adjust as needed
bat_range = (2,4.3)

show_enabled = True
save_enabled = False
save_prefix = "Skenario_15_03"
save_path = "./saved/"
save_transparent = False
save_dpi = 300

"""
# Create a 3D Isometric View Plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the trajectory
ax.plot(x_log, y_log, z_log, label="Drone Trajectory", color='blue', marker='o', linewidth=1)
ax.scatter(x_log, y_log, z_log, color='red', label="Waypoints", s=10)  # Optional waypoints

# Set the same viewing range for all axes
ax.set_xlim(*x_range)
ax.set_ylim(*y_range)
ax.set_zlim(*z_range)

# Add labels and legend
ax.set_xlabel("X Log")
ax.set_ylabel("Y Log")
ax.set_zlabel("Z Log")
ax.set_title("Drone Trajectory - Isometric Views")
ax.legend()
"""

# Generate isometric views
angles = [225,135,45,315]
for angle in angles:
    # Create a 3D Isometric View Plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the trajectory
    ax.plot(x_log, y_log, z_log, label="3D Drone Trajectory", color='blue', marker='o', linewidth=1)
    ax.scatter(x_log, y_log, z_log, color='red', label="Waypoints", s=10)  # Optional waypoints

    # Set the same viewing range for all axes
    ax.set_xlim(*x_range)
    ax.set_ylim(*y_range)
    ax.set_zlim(*z_range)

    # Add labels and legend
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("3D Drone Trajectory")
    ax.legend()
    ax.view_init(elev=30, azim=angle)
    plt.title(f"{save_prefix} Isometric View: Azimuth {angle}")
    if save_enabled:
        output_filename = f"{save_path}{save_prefix}_3D_iso_azimuth_{angle}.png"
        plt.savefig(output_filename, dpi=save_dpi, bbox_inches='tight', transparent=save_transparent)
    if show_enabled:
        plt.show()

# Create a 2D View
# X-Y
plt.figure()
plt.plot(x_log, y_log, label="X-Y Trajectory", color='blue', linewidth=1)
plt.scatter(x_log, y_log, color='red', label="Waypoints", s=10)  # Optional waypoints
plt.xlabel("x")
plt.ylabel("y")
plt.title(f"{save_prefix} Drone Trajectory X-Y (Top-Down View)")
plt.xlim(*x_range)
plt.ylim(*y_range)
plt.legend()
plt.grid(True)
if save_enabled:
    output_filename = f"{save_path}{save_prefix}_2D_XY.png"
    plt.savefig(output_filename, dpi=save_dpi, bbox_inches='tight', transparent=save_transparent)
if show_enabled:
    plt.show()
# X-Z
plt.figure()
plt.plot(x_log, z_log, label="X-Z Trajectory", color='blue', linewidth=1)
plt.scatter(x_log, z_log, color='red', label="Waypoints", s=10)  # Optional waypoints
plt.xlabel("x")
plt.ylabel("z")
plt.title(f"{save_prefix} Drone Trajectory X-Z")
plt.xlim(*x_range)
plt.ylim(*z_range)
plt.legend()
plt.grid(True)
if save_enabled:
    output_filename = f"{save_path}{save_prefix}_2D_XZ.png"
    plt.savefig(output_filename, dpi=save_dpi, bbox_inches='tight', transparent=save_transparent)
if show_enabled:
    plt.show()
# Y-Z
plt.figure()
plt.plot(y_log, z_log, label="Y-Z Trajectory", color='blue', linewidth=1)
plt.scatter(y_log, z_log, color='red', label="Waypoints", s=10)  # Optional waypoints
plt.xlabel("y")
plt.ylabel("z")
plt.title(f"{save_prefix} Drone Trajectory Y-Z")
plt.xlim(*y_range)
plt.ylim(*z_range)
plt.legend()
plt.grid(True)
if save_enabled:
    output_filename = f"{save_path}{save_prefix}_2D_YZ.png"
    plt.savefig(output_filename, dpi=save_dpi, bbox_inches='tight', transparent=save_transparent)
if show_enabled:
    plt.show()

# Battery
plt.figure()
plt.plot(et, bat, label="battery", color='blue', linewidth=1)
plt.scatter(et, bat, color='red', label="points", s=10)  # Optional waypoints
plt.xlabel("elapsed time (ms)")
plt.ylabel("battery (V)")
plt.title(f"{save_prefix} Battery")
plt.ylim(*bat_range)
plt.legend()
plt.grid(True)
if save_enabled:
    output_filename = f"{save_path}{save_prefix}_battery.png"
    plt.savefig(output_filename, dpi=save_dpi, bbox_inches='tight', transparent=save_transparent)
if show_enabled:
    plt.show()