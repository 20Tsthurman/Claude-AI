"""This file is the main entry point of your backend application.
It sets up a Flask server and defines the API endpoints for handling chat requests.
The /api/chat endpoint receives a POST request with the user's message, processes it using the process_message function from chatbot.py, and returns the chatbot's response as JSON."""


from flask import Flask, request, jsonify, send_from_directory
from chatbot import process_message
import os

app = Flask(__name__, static_folder='../frontend')

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/app.js')
def serve_app_js():
    return send_from_directory(app.static_folder, 'app.js')

@app.route('/api/chat', methods=['POST'])
def chat():
    message = request.json['message']
    response = process_message(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run()