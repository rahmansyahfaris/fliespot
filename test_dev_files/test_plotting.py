import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Read the file
data = pd.read_csv('../logs/log_cs_2024_11_20_15_30_17.txt', sep=',')

# Extract columns
x_log = data['x_log']
y_log = data['y_log']
et = data['et']

colors = ['green' if t <= 13840
          else 'red' if t <= 24400
          else 'blue' if t <= 32500
          else 'red' if t <= 42400
          else 'black' if t <= 50000
          else 'green' if t <= 42400
          else 'blue' if t <= 53300
          else 'green' if t <= 58700
          else 'yellow'
          for t in et]  # Blue for t <= 50, Red for t > 50

# Create a scatter plot
plt.scatter(x_log, y_log, label='Movements', c=colors, s=2)

# Set axis labels and title
plt.xlabel('x')
plt.ylabel('y')
plt.title('Logging Plot')

blue_patch = mpatches.Patch(color='blue', label='Time ≤ 50')
red_patch = mpatches.Patch(color='red', label='Time > 50')
plt.legend(handles=[blue_patch, red_patch])

# Set axis limits


# Add a legend
plt.legend()

# Show the plot
plt.show()
