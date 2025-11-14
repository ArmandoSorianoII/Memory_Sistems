import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import psutil
import logging
from collections import deque
from datetime import datetime
import sys
import os
import ctypes

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Windows-specific memory monitoring
if os.name == 'nt':
    class PERFORMANCE_INFORMATION(ctypes.Structure):
        _fields_ = [
            ('cb', ctypes.c_ulong),
            ('CommitTotal', ctypes.c_size_t),
            ('CommitLimit', ctypes.c_size_t),
            ('CommitPeak', ctypes.c_size_t),
            ('PhysicalTotal', ctypes.c_size_t),
            ('PhysicalAvailable', ctypes.c_size_t),
            ('SystemCache', ctypes.c_size_t),  # Standby memory
            ('KernelTotal', ctypes.c_size_t),
            ('KernelPaged', ctypes.c_size_t),
            ('KernelNonpaged', ctypes.c_size_t),
            ('PageSize', ctypes.c_size_t),
            ('HandleCount', ctypes.c_ulong),
            ('ProcessCount', ctypes.c_ulong),
            ('ThreadCount', ctypes.c_ulong),
        ]
    GetPerformanceInfo = ctypes.windll.psapi.GetPerformanceInfo

# Initialize the Dash app
app = dash.Dash(__name__)

# Store last 20 data points for each metric
history = {
    'ram': deque(maxlen=20),
    'cpu': deque(maxlen=20),
    'disk': deque(maxlen=20),
    'swap': deque(maxlen=20),
    'cache': deque(maxlen=20),
    'time': deque(maxlen=20)
}

# Initialize CPU measurement
psutil.cpu_percent(interval=None)

def get_system_stats():
    try:
        memory = psutil.virtual_memory()
        ram = memory.percent
        
        # Cache memory calculation
        cache_bytes = 0.0
        
        if os.name == 'nt':
            # Windows: Use Windows API for cache info
            perf_info = PERFORMANCE_INFORMATION()
            perf_info.cb = ctypes.sizeof(perf_info)
            if GetPerformanceInfo(ctypes.byref(perf_info), perf_info.cb):
                cache_bytes = perf_info.SystemCache * perf_info.PageSize
        
        elif hasattr(memory, 'cached'):
            # Linux/macOS: Use psutil's method
            cache_bytes = memory.cached
            
        cache = (cache_bytes / memory.total) * 100 if memory.total > 0 else 0
        
        swap = psutil.swap_memory()
        swap_percent = swap.percent
        cpu = psutil.cpu_percent(interval=None)
        disk = psutil.disk_usage('/').percent

        return {
            'RAM Usage (%)': ram,
            'CPU Usage (%)': cpu,
            'Disk Usage (%)': disk,
            'Swap Usage (%)': swap_percent,
            'Cache Usage (RAM) (%)': cache
        }
    except Exception as e:
        logging.error(f"Error fetching system stats: {e}")
        return {}

# Default to multiple graphs mode unless 'one' is specified
mode = sys.argv[1] if len(sys.argv) > 1 else 'multiple'

if mode == 'one':
    app.layout = html.Div([
        html.H1('System Monitoring Dashboard (Combined Graph)'),

        # Combined Line Chart
        dcc.Graph(id='combined-graph'),

        # Interval for updating the dashboard every 5 seconds
        dcc.Interval(
            id='interval-component',
            interval=2*1000,  # 2000 milliseconds (2 seconds)
            n_intervals=0
        )
    ])

    # Callback for combined graph updates
    @app.callback(
        Output('combined-graph', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_combined_graph(n):
        # Fetch system stats
        data = get_system_stats()

        if not data:
            logging.info("No data fetched")
            return {}

        # Log fetched data in the terminal
        logging.info(f"Fetched data: {data}")

        # Append the current time and all metrics to history
        current_time = datetime.now().strftime('%H:%M:%S')
        history['ram'].append(data['RAM Usage (%)'])
        history['cpu'].append(data['CPU Usage (%)'])
        history['disk'].append(data['Disk Usage (%)'])
        history['swap'].append(data['Swap Usage (%)'])
        history['cache'].append(data['Cache Usage (RAM) (%)'])
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
                ),
                go.Scatter(
                    x=list(history['time']),
                    y=list(history['swap']),
                    mode='lines+markers',
                    name='Swap Usage (%)'
                ),
                go.Scatter(
                    x=list(history['time']),
                    y=list(history['cache']),
                    mode='lines+markers',
                    name='Cache Usage (RAM) (%)'
                )
            ],
            'layout': go.Layout(
                title='System Usage Over Time',
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),
                yaxis=dict(title='Percentage'),
            )
        }

        return combined_figure

else:
    # Layout for multiple graphs
    app.layout = html.Div([
        html.H1('System Monitoring Dashboard (Separate Graphs)'),

        dcc.Graph(id='ram-usage-graph'),
        dcc.Graph(id='cpu-usage-graph'),
        dcc.Graph(id='disk-usage-graph'),
        dcc.Graph(id='swap-usage-graph'),
        dcc.Graph(id='cache-usage-graph'),

        # Interval for updating the dashboard every 5 seconds
        dcc.Interval(
            id='interval-component',
            interval=2*1000,  # 2000 milliseconds (2 seconds)
            n_intervals=0
        )
    ])

    # Callback for separate graph updates
    @app.callback(
        [Output('ram-usage-graph', 'figure'),
         Output('cpu-usage-graph', 'figure'),
         Output('disk-usage-graph', 'figure'),
         Output('swap-usage-graph', 'figure'),
         Output('cache-usage-graph', 'figure')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_separate_graphs(n):
        # Fetch system stats
        data = get_system_stats()

        if not data:
            logging.info("No data fetched")
            return {}, {}, {}, {}, {}  # Return empty dicts on error

        # Log fetched data in the terminal
        logging.info(f"Fetched data: {data}")

        # Append the current time and all metrics to history
        current_time = datetime.now().strftime('%H:%M:%S')
        history['ram'].append(data['RAM Usage (%)'])
        history['cpu'].append(data['CPU Usage (%)'])
        history['disk'].append(data['Disk Usage (%)'])
        history['swap'].append(data['Swap Usage (%)'])   # NUEVO
        history['cache'].append(data['Cache Usage (RAM) (%)']) # NUEVO
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
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),
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
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),
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
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),
                yaxis=dict(title='Percentage'),
            )
        }
        
        

        # Create Swap Usage Line Chart
        swap_figure = {
            'data': [go.Scatter(
                x=list(history['time']),
                y=list(history['swap']),
                mode='lines+markers',
                name='Swap Usage (%)'
            )],
            'layout': go.Layout(
                title='Swap (Virtual Memory) Usage Over Time',
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),
                yaxis=dict(title='Percentage'),
            )
        }

        # Create Cache Usage Line Chart
        cache_figure = {
            'data': [go.Scatter(
                x=list(history['time']),
                y=list(history['cache']),
                mode='lines+markers',
                name='Cache Usage (RAM) (%)'
            )],
            'layout': go.Layout(
                title='Cache Usage (RAM) Over Time',
                xaxis=dict(title='Time', tickformat='%H:%M:%S'),
                yaxis=dict(title='Percentage'),
            )
        }

        return ram_figure, cpu_figure, disk_figure, swap_figure, cache_figure

# Run the app
if __name__ == '__main__':
    app.run(debug=True)