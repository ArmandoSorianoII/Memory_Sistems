import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import psutil
import logging
from collections import deque
from datetime import datetime
import sys

# Set up basic logging to debug
logging.basicConfig(level=logging.INFO)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define fixed-size lists (deque) to store the last 20 data points for RAM, CPU, Disk usage, and time
history = {
    'ram': deque(maxlen=20),
    'cpu': deque(maxlen=20),
    'disk': deque(maxlen=20),
    'time': deque(maxlen=20)  # Store timestamps for x-axis
}

# Function to get system statistics (RAM, CPU, and Disk)
def get_system_stats():
    try:
        # Get memory stats
        memory = psutil.virtual_memory()
        ram = memory.percent

        # Get CPU usage
        cpu = psutil.cpu_percent(interval=1)

        # Get Disk usage
        disk = psutil.disk_usage('/').percent

        # Return RAM, CPU, and Disk data
        return {
            'RAM Usage (%)': ram,
            'CPU Usage (%)': cpu,
            'Disk Usage (%)': disk
        }
    except Exception as e:
        logging.error(f"Error fetching system stats: {e}")
        return {}

# Determine whether to run in 'one' or 'multiple' mode based on command-line argument
mode = sys.argv[1] if len(sys.argv) > 1 else 'multiple'

if mode == 'one':
    app.layout = html.Div([
        html.H1('System Monitoring Dashboard (Combined Graph)'),

        # Combined Line Chart for RAM, CPU, and Disk
        dcc.Graph(id='combined-graph'),

        # Interval for updating the dashboard every 5 seconds
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # 5000 milliseconds (5 seconds)
            n_intervals=0
        )
    ])

    # Update callback to refresh the combined RAM, CPU, and Disk usage graph every interval
    @app.callback(
        Output('combined-graph', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_combined_graph(n):
        # Fetch system stats (RAM, CPU, and Disk)
        data = get_system_stats()

        if not data:
            logging.info("No data fetched")
            return {}

        # Log fetched data in the terminal
        logging.info(f"Fetched data: {data}")

        # Append the current time, RAM, CPU, and Disk usage to history
        current_time = datetime.now().strftime('%H:%M:%S')  # Get the current time as a string
        history['ram'].append(data['RAM Usage (%)'])
        history['cpu'].append(data['CPU Usage (%)'])
        history['disk'].append(data['Disk Usage (%)'])
        history['time'].append(current_time)

        # Create Combined Line Chart
        combined_figure = {
            'data': [
                go.Scatter(
                    x=list(history['time']),
                    y=list(history['ram']),
                    mode='lines+markers',
                    name='RAM Usage (%)'
                ),
                go.Scatter(
                    x=list(history['time']),
                    y=list(history['cpu']),
                    mode='lines+markers',
                    name='CPU Usage (%)'
                ),
                go.Scatter(
                    x=list(history['time']),
                    y=list(history['disk']),
                    mode='lines+markers',
                    name='Disk Usage (%)'
                )
            ],
            'layout': go.Layout(
                title='RAM, CPU, and Disk Usage Over Time',
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),  # Format the time
                yaxis=dict(title='Percentage'),
            )
        }

        return combined_figure

else:
    # Layout for multiple graphs (RAM, CPU, Disk each on its own graph)
    app.layout = html.Div([
        html.H1('System Monitoring Dashboard (Separate Graphs)'),

        # RAM Usage Line Chart
        dcc.Graph(id='ram-usage-graph'),

        # CPU Usage Line Chart
        dcc.Graph(id='cpu-usage-graph'),

        # Disk Usage Line Chart
        dcc.Graph(id='disk-usage-graph'),

        # Interval for updating the dashboard every 5 seconds
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # 5000 milliseconds (5 seconds)
            n_intervals=0
        )
    ])

    # Update callback to refresh the RAM, CPU, and Disk usage graphs every interval
    @app.callback(
        [Output('ram-usage-graph', 'figure'),
         Output('cpu-usage-graph', 'figure'),
         Output('disk-usage-graph', 'figure')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_separate_graphs(n):
        # Fetch system stats (RAM, CPU, and Disk)
        data = get_system_stats()

        if not data:
            logging.info("No data fetched")
            return {}, {}, {}

        # Log fetched data in the terminal
        logging.info(f"Fetched data: {data}")

        # Append the current time, RAM, CPU, and Disk usage to history
        current_time = datetime.now().strftime('%H:%M:%S')  # Get the current time as a string
        history['ram'].append(data['RAM Usage (%)'])
        history['cpu'].append(data['CPU Usage (%)'])
        history['disk'].append(data['Disk Usage (%)'])
        history['time'].append(current_time)

        # Create RAM Usage Line Chart
        ram_figure = {
            'data': [go.Scatter(
                x=list(history['time']),
                y=list(history['ram']),
                mode='lines+markers',
                name='RAM Usage (%)'
            )],
            'layout': go.Layout(
                title='RAM Usage Over Time',
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),  # Format the time
                yaxis=dict(title='Percentage'),
            )
        }

        # Create CPU Usage Line Chart
        cpu_figure = {
            'data': [go.Scatter(
                x=list(history['time']),
                y=list(history['cpu']),
                mode='lines+markers',
                name='CPU Usage (%)'
            )],
            'layout': go.Layout(
                title='CPU Usage Over Time',
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),  # Format the time
                yaxis=dict(title='Percentage'),
            )
        }

        # Create Disk Usage Line Chart
        disk_figure = {
            'data': [go.Scatter(
                x=list(history['time']),
                y=list(history['disk']),
                mode='lines+markers',
                name='Disk Usage (%)'
            )],
            'layout': go.Layout(
                title='Disk Usage Over Time',
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),  # Format the time
                yaxis=dict(title='Percentage'),
            )
        }

        return ram_figure, cpu_figure, disk_figure

# Run the app
if __name__ == '__main__':
    app.run(debug=True)