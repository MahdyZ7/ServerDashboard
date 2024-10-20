import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import *
import time
import os
from dotenv import load_dotenv

# Set page config
st.set_page_config(page_title="Server Monitoring Dashboard", layout="wide")

# Initialize database
init_db()

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_server_data():
    servers = []
    for i in range(6):
        server_name = os.getenv(f"SERVER{i}_NAME")
        # st.write(server_name)
        # st.write("ASASAS")
        if server_name:
            servers.append({
                'name': server_name,
                'host': os.getenv(f"SERVER{i}_HOST"),
                'username': os.getenv(f"SERVER{i}_USERNAME"),
                'password': os.getenv(f"SERVER{i}_PASSWORD")
            })
    return servers

if 'servers' not in st.session_state:
    st.session_state.servers = get_server_data()
    # You can update existing servers or add new ones here if needed
else:
    pass
    

if 'metrics' not in st.session_state:
    st.session_state.metrics = {server['name']: {} for server in st.session_state.servers}

# Populate mock data if not already done
if 'mock_data_populated' not in st.session_state:
    populate_mock_data([server['name'] for server in st.session_state.servers])
    st.session_state.mock_data_populated = True

# Define alert thresholds
ALERT_THRESHOLDS = {
    'cpu_percent': 90.0,
    'memory_percent': 90.0,
    'disk_percent': 90.0
}

# Dashboard title
st.title("Server Monitoring Dashboard")

# Create a 2x3 grid for server metrics
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)
columns = [col1, col2, col3, col4, col5, col6]

def update_metrics():
    for server in st.session_state.servers:
        # print(f"Server {server}")
        metrics = get_metrics(server)
        top_users = generate_mock_top_users()
        st.session_state.metrics[server['name']] = {**metrics, 'top_users': top_users}
        store_metrics(server['name'], metrics)

def check_alerts(metrics):
    alerts = []
    for metric, value in metrics.items():
        if metric in ALERT_THRESHOLDS and value > ALERT_THRESHOLDS[metric]:
            alerts.append(f"{metric.replace('_', ' ').title()} exceeds threshold: {value:.1f}% (Threshold: {ALERT_THRESHOLDS[metric]}%)")
    return alerts

def display_metrics():
    for server, column in zip(st.session_state.servers, columns):
        with column:
            st.subheader(server['name'])
            metrics = st.session_state.metrics[server['name']]
            
            # Check for alerts
            alerts = check_alerts(metrics)
            if alerts:
                for alert in alerts:
                    st.warning(alert)
            
            # CPU usage gauge
            fig_cpu = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['cpu_percent'],
                title={'text': "CPU Usage"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 80], 'color': "gray"},
                           {'range': [80, 100], 'color': "red"}],
                       'threshold': {
                           'line': {'color': "red", 'width': 4},
                           'thickness': 0.75,
                           'value': ALERT_THRESHOLDS['cpu_percent']}}))
            fig_cpu.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig_cpu, use_container_width=True, config={'staticPlot': True})

            # Memory usage bar
            fig_mem = go.Figure(go.Bar(
                x=[metrics['memory_percent']],
                y=['Memory'],
                orientation='h',
                text=[f"{metrics['memory_percent']:.1f}%"],
                textposition='auto',
                marker=dict(color='lightblue', line=dict(color='darkblue', width=2))
            ))
            fig_mem.update_layout(height=100, margin=dict(l=10, r=10, t=10, b=10), xaxis_range=[0, 100])
            st.plotly_chart(fig_mem, use_container_width=True, config={'staticPlot': True})

            # Disk usage bar
            fig_disk = go.Figure(go.Bar(
                x=[metrics['disk_percent']],
                y=['Disk'],
                orientation='h',
                text=[f"{metrics['disk_percent']:.1f}%"],
                textposition='auto',
                marker=dict(color='lightgreen', line=dict(color='darkgreen', width=2))
            ))
            fig_disk.update_layout(height=100, margin=dict(l=10, r=10, t=10, b=10), xaxis_range=[0, 100])
            st.plotly_chart(fig_disk, use_container_width=True, config={'staticPlot': True})

            # Top users table
            st.text(f"# Physical CPUs	: {metrics['pcpu']}")
            st.text(f"# Virtual CPUs	: {metrics['vcpu']}")
            st.text(f"Memory Usage	: {metrics['memory_ratio']} ({metrics['memory_percent']}%)")
            st.text(f"Disk Usage	: {metrics['disk_ratio']} ({metrics['disk_percent']}%)")
            st.text(f"CPU Load	: {metrics['cpu_percent']}%")
            st.text(f"Last Boot	: {metrics['last_boot']}")
            st.text(f"TCP Connections	: {metrics['tcp']} established")
            st.text(f"Users logged	: {metrics['users']}")
            # st.subheader("Top Resource Users")
            # df_users = pd.DataFrame(metrics['top_users'])
            # st.dataframe(df_users, use_container_width=True)

            # # Historical data
            # st.subheader("Historical Data (24 hours)")
            # hist_data = get_historical_data(server['name'])
            # if not hist_data.empty:
            #     fig_hist = px.line(hist_data, x='timestamp', y=['cpu_percent', 'memory_percent', 'disk_percent'],
            #                        labels={'value': 'Percentage', 'variable': 'Metric'},
            #                        title='Resource Usage Over Time')
            #     fig_hist.update_layout(legend_title_text='Metric', height=300)
            #     st.plotly_chart(fig_hist, use_container_width=True, config={'staticPlot': True})
            # else:
            #     with st.spinner("Collecting historical data..."):
            #         time.sleep(2)  # Simulate data collection
            #     st.info("Historical data is being collected. Please wait or refresh the page.")

# Main app logic
update_metrics()
display_metrics()

# Auto-refresh
if st.button('Refresh'):
    update_metrics()
    display_metrics()

def schedule_auto_refresh(interval_in_seconds):
    while True:
        time.sleep(interval_in_seconds * 60)  # Convert seconds to minutes
        st.rerun()
schedule_auto_refresh(30)