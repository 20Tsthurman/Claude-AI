import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import mysql.connector
from pdfminer.high_level import extract_text
import docx

app = Flask(__name__, static_folder='../frontend')

# MySQL database connection configuration
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Tst809024-",  # Your MySQL password
        database="chatbotdb"  # The name of the MySQL database you created
    )

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/app.js')
def serve_app_js():
    return send_from_directory(app.static_folder, 'app.js')

@app.route('/api/chat', methods=['POST'])
def chat():
    message = request.json['message']
    # Assume a function `process_message` is defined elsewhere that handles the chat response
    response = process_message(message)
    return jsonify({'response': response})

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Determine the file type and extract text accordingly
        text_content = ""
        if filename.endswith('.pdf'):
            text_content = extract_text(file_path)  # Using pdfminer.six for PDF text extraction
        elif filename.endswith('.docx'):
            text_content = extract_text_from_docx(file_path)  # Using python-docx for DOCX text extraction
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        # Here you would add logic to handle the extracted text content
        # For demonstration, we're just sending it back in the response
        return jsonify({'message': 'File uploaded and processed successfully', 'content': text_content}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

# Define your /api/documents, /api/documents/<int:document_id>, and other routes here

# Example placeholder for process_message function
def process_message(message):
    # Placeholder logic for processing messages
    return "Message processing not implemented."

if __name__ == '__main__':
    app.run(debug=True)
