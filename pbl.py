

from flask import Flask, render_template, request, jsonify
from collections import deque

app = Flask(__name__)

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority

processes = []
process_queue = deque()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_process', methods=['POST'])
def add_process():
    pid = len(processes) + 1
    data = request.get_json()
    arrival_time = data.get('arrival_time')
    burst_time = data.get('burst_time')
    priority = data.get('priority')

    if priority is not None:
        processes.append(Process(pid, arrival_time, burst_time, priority))
    else:
        processes.append(Process(pid, arrival_time, burst_time))
    return jsonify({"status": "success"})

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    algorithm = data.get('algorithm')
    process_queue.clear()
    for process in processes:
        # Reset remaining_time for each new simulation
        process.remaining_time = process.burst_time
        process_queue.append(process)

    if algorithm == "FCFS":
        logs, timeline = run_fcfs()
    else:
        logs, timeline = (["Algorithm not implemented in demo."], [])

    return jsonify({"log": logs, "timeline": timeline})


def run_fcfs():
    current_time = 0
    logs = []
    timeline = []

    sorted_processes = sorted(process_queue, key=lambda p: p.arrival_time)

    for proc in sorted_processes:
        start = max(current_time, proc.arrival_time)
        end = start + proc.burst_time
        logs.append(f"Process {proc.pid} started at time {start}.")
        logs.append(f"Process {proc.pid} finished at time {end}.")
        timeline.append({'pid': proc.pid, 'start': start, 'end': end})
        current_time = end

    return logs, timeline

if __name__ == '__main__':
    app.run(debug=True)
