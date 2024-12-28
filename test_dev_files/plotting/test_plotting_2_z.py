import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Read the file
data = pd.read_csv('../logs/log_cs_2024_11_20_15_30_17.txt', sep=',')

# Extract columns
x_log = data['x_log']
y_log = data['y_log']
z_log = data['z_log']
bat = data['bat']
et = data['et']


# Create a scatter plot
plt.plot(et, bat, label='Movements', c='red')

# Set axis labels and title
plt.xlabel('t')
plt.ylabel('bat')
plt.title('Logging Plot')

# Add a legend
plt.legend()

# Show the plot
plt.show()
