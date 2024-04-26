import os
import docx
from pdfminer.high_level import extract_text
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Tst809024-",
        database="chatbotdb"
    )

def process_uploaded_file(file_path, class_details):
    file_extension = file_path.rsplit('.', 1)[1].lower()
    
    if file_extension == 'pdf':
        text = extract_text(file_path)
    elif file_extension in ['doc', 'docx']:
        doc = docx.Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    else:
        with open(file_path, 'r') as file:
            text = file.read()
    
    store_document_info(file_path, text, class_details)

def store_document_info(file_path, text, class_details):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS documents (id INT AUTO_INCREMENT PRIMARY KEY, file_path VARCHAR(255), content TEXT)")
    cursor.execute("INSERT INTO documents (file_path, content) VALUES (%s, %s)", (file_path, text))
    document_id = cursor.lastrowid
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            class_name VARCHAR(255),
            times VARCHAR(255),
            document_id INT,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_topics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            class_name VARCHAR(255),
            topic VARCHAR(255),
            description TEXT,
            document_id INT,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)
    for detail in class_details:
        cursor.execute("INSERT INTO class_info (class_name, times, document_id) VALUES (%s, %s, %s)",
                       (detail['class_name'], detail['times'], document_id))
        cursor.execute("INSERT INTO class_topics (class_name, topic, description, document_id) VALUES (%s, %s, %s, %s)",
                       (detail['class_name'], detail['topic'], detail['description'], document_id))
    conn.commit()
    conn.close()
    print(f"Document and class details stored: {file_path}")
