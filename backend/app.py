import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import mysql.connector
from pdfminer.high_level import extract_text
import docx
import re
import time
import anthropic
from config import API_KEY

app = Flask(__name__, static_folder='../frontend')
client = anthropic.Anthropic(api_key=API_KEY)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Tst809024-",
        database="chatbotdb"
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
        text_content = ""
        if filename.endswith('.pdf'):
            text_content = extract_text(file_path)
        elif filename.endswith('.docx'):
            text_content = extract_text_from_docx(file_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        return jsonify({'message': 'File uploaded and processed successfully', 'content': text_content}), 200
    return jsonify({'error': 'Invalid file type'}), 400

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

@app.route('/api/documents', methods=['GET'])
def get_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    conn.close()
    return jsonify({'documents': [{'id': doc[0], 'file_path': doc[1], 'content': doc[2]} for doc in documents]})

def extract_class_name(message):
    match = re.search(r"\b([A-Z]{2,4}\d{3})\b", message, re.I)
    if match:
        return match.group(1)
    else:
        return None

def extract_topic(message):
    keywords = {
        "variables and data types": ["variables and data types"],
        "control structures": ["control structures", "if else", "loops"],
        "functions": ["functions"],
        "arrays": ["arrays"],
        "input output": ["input", "output"],
        "file handling": ["file handling", "read file", "write file"],
        "object-oriented programming": ["object-oriented programming", "oop", "classes", "objects"],
        "debugging": ["debugging"],
        "algorithms": ["algorithms", "problem solving"]
    }
    for topic, topic_keywords in keywords.items():
        for keyword in topic_keywords:
            if keyword in message.lower():
                return topic
    return None

def get_class_info(class_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT class_name, times FROM class_info WHERE class_name LIKE %s"
    cursor.execute(query, ("%" + class_name + "%",))
    result = cursor.fetchone()
    conn.close()

    if result:
        return f"{result[0]} class is scheduled at {result[1]}."
    else:
        return f"I couldn't find the class time for {class_name}. Please check the class name and try again."

def get_class_topics(class_name, topic=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if topic:
        query = "SELECT description FROM class_topics WHERE class_name = %s AND topic = %s"
        cursor.execute(query, (class_name, topic))
        result = cursor.fetchone()
        conn.close()

        if result:
            return f"In {class_name}, we learned the following about {topic}:\n{result[0]}"
        else:
            return f"I couldn't find information about {topic} for the class {class_name}. Please make sure the topic is covered in the class and try again."
    else:
        query = "SELECT topic, description FROM class_topics WHERE class_name = %s"
        cursor.execute(query, (class_name,))
        results = cursor.fetchall()
        conn.close()

        if results:
            response = f"In {class_name}, we learned about the following topics:\n"
            for result in results:
                topic, description = result
                response += f"- {topic}: {description}\n"
            return response
        else:
            return f"I couldn't find any topics for the class {class_name}. Please make sure the class name is correct and try again."

def process_message(message):
    system_message = """
    You are an AI assistant named WKU Course Aid, created by Western Kentucky University. Your purpose is to assist students with various aspects of their academic life at WKU.

    Key responsibilities:
    1. Help students understand their course work by providing explanations, clarifications, and examples related to specific topics or assignments.
    2. Assist students in calculating their grades based on the grading policies and criteria set by their instructors.
    3. Provide information about class schedules, including the days, times, and locations of specific courses.
    4. Answer general questions about WKU's academic policies, resources, and support services.
    5. You are allowed to answer questions related to how to do something. Such as how to solve a math question. 
    6. You can use the web scraped data to answer questions that are asked related to online information.
    7. You can use uploaded files in the MySQL database to help assist in answering questions.
    
    When responding to students:
    - Be friendly, patient, and encouraging.
    - Provide clear and concise explanations tailored to the student's needs and level of understanding.
    - If a student asks about a specific course, assignment, or grade calculation, request additional context or details to provide accurate guidance.
    - Maintain student privacy by not asking for or revealing any personal information.
    - If you don't have the necessary information to answer a question, direct the student to the appropriate WKU resource or department.
    - Provide concise and directly relevant answers to their questions.
    - Avoid including unnecessary details or context that doesn't address the specific question.
    - If a question is unclear or lacks sufficient information, ask for clarification before providing an answer.
    
    Remember, your goal is to support students' academic success and help them navigate their educational journey at WKU effectively.
    """
    if "what time is" in message.lower() or "when does" in message.lower() or "class" in message.lower():
        class_name = extract_class_name(message)
        if class_name:
            return get_class_info(class_name)
        else:
            return "I couldn't find the class name in your question. Please provide the class name or code."

    if "what did we learn about" in message.lower() or "in cs101" in message.lower():
        topic = extract_topic(message)
        if topic:
            return get_class_topics("CS101", topic)
        else:
            return "I couldn't find the topic in your question. Please provide the topic you want to know about."

    if "what did we learn" in message.lower() and "cs101" in message.lower():
        return get_class_topics("CS101")

    keywords = ["about", "academics", "courses", "calendar"]
    relevant_keyword = next((keyword for keyword in keywords if keyword in message.lower()), None)

    if relevant_keyword:
        conn = get_db_connection()
        cursor = conn.cursor()
        retry_count = 3
        result = None

        while retry_count > 0:
            try:
                query = "SELECT title, content FROM scraped_data WHERE url LIKE %s ORDER BY timestamp DESC LIMIT 1"
                cursor.execute(query, (f"%{relevant_keyword}%",))
                result = cursor.fetchone()
                break
            except mysql.connector.Error as e:
                print(f"Database error: {e}")
                retry_count -= 1
                time.sleep(1)

        if result:
            title, content = result
            response = f"Here's the relevant information from the WKU website:\nTitle: {title}\nContent: {content}"
        else:
            query = "SELECT file_path, content FROM documents WHERE content LIKE %s"
            cursor.execute(query, (f"%{relevant_keyword}%",))
            results = cursor.fetchall()

            if results:
                response = "Here's the relevant information from the uploaded documents:\n"
                for result in results:
                    file_path, content = result
                    response += f"- File: {file_path}\n  Content: {content}\n"
            else:
                response = "Sorry, I couldn't find any relevant information from the WKU website or uploaded documents for your query."

        conn.close()
    else:
        # response = client.completions.create(
        #     prompt=prompt,
        #     model="claude-2.1",
        #     max_tokens_to_sample=250,
        #     temperature=0.2,
        #     stop_sequences=[anthropic.HUMAN_PROMPT],
        # )
        # response = response.completion

        response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=250,
        temperature=0.2,
        system=system_message,
        messages=[
            {"role": "user", "content": message}
        ]
    )

    # Check if 'content' is present and process each TextBlock
    if response.content:
        response_text = ''
        for text_block in response.content:
            response_text += text_block.text + '\n'

        return response_text.strip()  # Trim the final newline character
    else:
        return "Sorry, I couldn't understand that."


if __name__ == '__main__':
    app.run(debug=True)