import paramiko
import psutil
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import random
import subprocess

def connect_to_server(hostname, username, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname=hostname, username=username, password=password, timeout=10)
        return ssh_client
    except Exception as e:
        print(f"Failed to connect to {hostname}: {str(e)}")
        return None

def get_server_metrics(ssh_client):
    try:
        stdin, stdout, stderr = ssh_client.exec_command("python3 -c 'import psutil; print(psutil.cpu_percent(), psutil.virtual_memory().percent, psutil.disk_usage(\"/\").percent)'")
        output = stdout.read().decode().strip().split()
        
        return {
            'cpu_percent': float(output[0]),
            'memory_percent': float(output[1]),
            'disk_percent': float(output[2])
        }
    except Exception as e:
        raise Exception(f"Failed to get server metrics: {str(e)}")

def get_top_users(ssh_client):
    try:
        stdin, stdout, stderr = ssh_client.exec_command("""
        ps aux --sort=-%cpu,%mem | awk 'NR<=6 {print $1,$3,$4,$11}' | column -t
        """)
        output = stdout.read().decode().strip().split('\n')
        
        users = []
        for line in output[1:]:  # Skip header
            user, cpu, mem, command = line.split(None, 3)
            users.append({
                'User': user,
                'CPU %': float(cpu),
                'Memory %': float(mem),
                'Command': command
            })
        
        return users
    except Exception as e:
        raise Exception(f"Failed to get top users: {str(e)}")

def init_db():
    conn = sqlite3.connect('server_metrics.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS metrics
                 (timestamp TEXT, server_name TEXT, cpu_percent REAL, memory_percent REAL, disk_percent REAL)''')
    conn.commit()
    conn.close()

def store_metrics(server_name, metrics):
    conn = sqlite3.connect('server_metrics.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO metrics VALUES (?, ?, ?, ?, ?)",
              (timestamp, server_name, metrics['cpu_percent'], metrics['memory_percent'], metrics['disk_percent']))
    conn.commit()
    conn.close()

def get_historical_data(server_name, hours=24):
    conn = sqlite3.connect('server_metrics.db')
    query = f"""
    SELECT timestamp, cpu_percent, memory_percent, disk_percent
    FROM metrics
    WHERE server_name = ?
    AND timestamp >= datetime('now', '-{hours} hours')
    ORDER BY timestamp
    """
    df = pd.read_sql_query(query, conn, params=(server_name,))
    conn.close()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Mock data generation functions
def get_metrics(server):
    try:
        command_string = ["./BashGetInfo.sh", server['host'], server['username'], server['password'], "mini_monitering.sh"]
        result = subprocess.run(command_string, capture_output=True, text=True, check=True)
        parsed_results = (result.stdout).split(sep=',')
        return {
            'arch': parsed_results[0],
            'pcpu': parsed_results[1],
            'vcpu': parsed_results[2],
            'memory_ratio': parsed_results[3],
            'memory_percent': float(parsed_results[4]),
            'disk_ratio': parsed_results[5],
            'disk_percent': float(parsed_results[6].strip('%')),
            'cpu_percent': float(parsed_results[7].strip('%')),
            'last_boot': parsed_results[8],
            'tcp': parsed_results[9],
            'users': parsed_results[10]
        }
    except Exception as e:
        print(f"Failed to get metric: {str(e)}")
    return {
		'cpu_percent': random.uniform(0, 100),
		'memory_percent': random.uniform(0, 100),
		'disk_percent': random.uniform(0, 100)
	}

def generate_mock_metrics():
    return {
        'cpu_percent': random.uniform(0, 100),
        'memory_percent': random.uniform(0, 100),
        'disk_percent': random.uniform(0, 100)
    }

def generate_mock_top_users():
    users = ['user1', 'user2', 'user3', 'user4', 'user5']
    commands = ['python', 'nginx', 'mysql', 'apache2', 'nodejs']
    return [
        {
            'User': random.choice(users),
            'CPU %': random.uniform(0, 20),
            'Memory %': random.uniform(0, 20),
            'Command': random.choice(commands)
        } for _ in range(5)
    ]

def generate_mock_historical_data(server_name, hours=24):
    now = datetime.now()
    data = []
    for i in range(hours * 6):  # Generate data points every 10 minutes
        timestamp = now - timedelta(minutes=i*10)
        metrics = generate_mock_metrics()
        data.append({
            'timestamp': timestamp,
            'server_name': server_name,
            'cpu_percent': metrics['cpu_percent'],
            'memory_percent': metrics['memory_percent'],
            'disk_percent': metrics['disk_percent']
        })
    return pd.DataFrame(data)

# Function to populate the database with mock data
def populate_mock_data(server_names, hours=24):
    conn = sqlite3.connect('server_metrics.db')
    c = conn.cursor()
    
    for server_name in server_names:
        mock_data = generate_mock_historical_data(server_name, hours)
        for _, row in mock_data.iterrows():
            c.execute("INSERT INTO metrics VALUES (?, ?, ?, ?, ?)",
                      (row['timestamp'].isoformat(), row['server_name'], row['cpu_percent'], row['memory_percent'], row['disk_percent']))
    
    conn.commit()
    conn.close()
