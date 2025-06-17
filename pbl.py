from flask import Flask, render_template, request, jsonify
from collections import deque

app = Flask(_name_)

class Process:
    def _init_(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority

processes = []

@app.route('/')
def index():
    return render_template('index.html')  # Ensure your index.html exists

@app.route('/add_process', methods=['POST'])
def add_process():
    data = request.get_json()
    arrival_time = data.get('arrival_time')
    burst_time = data.get('burst_time')
    priority = data.get('priority')  # Keeping for completeness, not used in SRTN

    pid = len(processes) + 1
    processes.append(Process(pid, arrival_time, burst_time, priority))
    return jsonify({"status": "success"})

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    algorithm = data.get('algorithm')
    time_quantum = data.get('time_quantum', 1)  # For RR, not used in SRTN

    # Reset remaining time before simulation
    for p in processes:
        p.remaining_time = p.burst_time
    
    if algorithm == "FCFS":
        logs, timeline = run_fcfs()
    elif algorithm == "SJF":
        logs, timeline = run_sjf()
    elif algorithm == "SRTN":
        logs, timeline = run_srtn()
    elif algorithm == "RR":
        try:
            tq = int(time_quantum)
        except Exception:
            tq = 1
        logs, timeline = run_rr(tq)
    else:
        logs, timeline = (["Algorithm not implemented."], [])
    
    return jsonify({"log": logs, "timeline": timeline})

def run_fcfs():
    current_time = 0
    logs = []
    timeline = []
    sorted_procs = sorted(processes, key=lambda p: p.arrival_time)
    
    for proc in sorted_procs:
        start = max(current_time, proc.arrival_time)
        end = start + proc.burst_time
        logs.append(f"Process {proc.pid} started at time {start}.")
        logs.append(f"Process {proc.pid} finished at time {end}.")
        timeline.append({"pid": proc.pid, "start": start, "end": end})
        current_time = end
    return logs, timeline

def run_sjf():
    current_time = 0
    logs = []
    timeline = []
    procs = sorted(processes, key=lambda p: (p.arrival_time, p.burst_time))
    
    while procs:
        available = [p for p in procs if p.arrival_time <= current_time]
        if available:
            proc = min(available, key=lambda p: p.burst_time)
            start = current_time
            end = start + proc.burst_time
            logs.append(f"Process {proc.pid} started at time {start}.")
            logs.append(f"Process {proc.pid} finished at time {end}.")
            timeline.append({"pid": proc.pid, "start": start, "end": end})
            current_time = end
            procs.remove(proc)
        else:
            current_time += 1
    return logs, timeline

def run_srtn():
    logs = []
    timeline = []
    n = len(processes)
    remaining = [p.burst_time for p in processes]
    completed = 0
    current_time = 0
    prev = -1
    start_times = [-1] * n
    end_times = [0] * n

    while completed < n:
        # Find process with minimum remaining time at current_time which has arrived
        min_remaining = float('inf')
        shortest = -1
        for i in range(n):
            if (processes[i].arrival_time <= current_time) and (remaining[i] > 0) and (remaining[i] < min_remaining):
                min_remaining = remaining[i]
                shortest = i
        
        if shortest == -1:
            # No process ready; increment time
            current_time += 1
            continue
        
        # If new process is starting execution, record start time
        if start_times[shortest] == -1:
            start_times[shortest] = current_time
            logs.append(f"Process {processes[shortest].pid} started at time {current_time}.")

        # Execute the process for 1 time unit
        remaining[shortest] -= 1
        current_time += 1

        # If process finished
        if remaining[shortest] == 0:
            completed += 1
            end_times[shortest] = current_time
            logs.append(f"Process {processes[shortest].pid} finished at time {current_time}.")
            timeline.append({"pid": processes[shortest].pid, "start": start_times[shortest], "end": end_times[shortest]})

    return logs, timeline

def run_rr(time_quantum):
    current_time = 0
    logs = []
    timeline = []
    queue = deque(processes)
    
    last_execution = {p.pid: None for p in processes}
    
    while queue:
        proc = queue.popleft()
        if proc.remaining_time > 0:
            start = current_time
            time_slice = min(proc.remaining_time, time_quantum)
            current_time += time_slice
            proc.remaining_time -= time_slice
            
            if proc.remaining_time == 0:
                logs.append(f"Process {proc.pid} finished at time {current_time}.")
                timeline.append({"pid": proc.pid, "start": start, "end": current_time})
            else:
                logs.append(f"Process {proc.pid} executed from time {start} to {current_time}.")
                queue.append(proc)
    return logs, timeline

if _name_ == '_main_':
    app.run(debug=True)
