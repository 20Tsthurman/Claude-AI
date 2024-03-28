import os
import psutil
import time
import threading
import queue  # Import the queue module
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.chatbot import process_message

def monitor_cpu_usage(stop_event, q, interval=0.1):
    while not stop_event.is_set():
        cpu_usage = psutil.cpu_percent(interval=interval)
        q.put(cpu_usage)

def measure_cpu_usage(message, interval=0.1):
    cpu_usage_samples = []
    q = queue.Queue()
    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_cpu_usage, args=(stop_event, q, interval), daemon=True)
    
    monitor_thread.start()
    start_time = time.time()
    # Process the message
    response = process_message(message)
    end_time = time.time()
    stop_event.set()
    monitor_thread.join()

    # Collect CPU usage samples from the queue
    while not q.empty():
        cpu_usage_samples.append(q.get())

    execution_time = end_time - start_time
    if cpu_usage_samples:  # Prevent division by zero
        average_cpu_usage = sum(cpu_usage_samples) / len(cpu_usage_samples)
    else:
        average_cpu_usage = 0.0

    return average_cpu_usage, execution_time

# Test with different input sizes
test_messages = [
    "Hello",
    "This is a test message.",
    "I need help with calculating my grade for CS101.",
    "Can you provide me with information about the course requirements for MATH201?",
]

print("Starting CPU usage test...")

for message in test_messages:
    print(f"Testing message: {message}")
    cpu_usage, execution_time = measure_cpu_usage(message, interval=0.1)
    print(f"Input size: {len(message)}, CPU Usage: {cpu_usage:.2f}%, Execution Time: {execution_time:.4f} seconds")

print("CPU usage test completed.")
