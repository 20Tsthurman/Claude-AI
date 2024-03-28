import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import time
from backend.chatbot import process_message


print("Starting performance test...")

def measure_execution_time(message):
    print(f"Measuring execution time for message: {message}")
    start_time = time.time()
    response = process_message(message)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.4f} seconds")
    return execution_time

# Test with different input sizes
test_messages = [
    "Hello",
    "This is a test message.",
    "I need help with calculating my grade for CS101.",
    "Can you provide me with information about the course requirements for MATH201?",
]

for message in test_messages:
    print(f"Testing message: {message}")
    execution_time = measure_execution_time(message)
    print(f"Input size: {len(message)}, Execution time: {execution_time:.4f} seconds")

print("Performance test completed.")