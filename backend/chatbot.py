import re
import time
import anthropic
import mysql.connector

# Assuming API_KEY is imported from a separate config module
from config import API_KEY

client = anthropic.Anthropic(api_key=API_KEY)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Create your own",
        database="chatbotdb"
    )

def extract_class_name(message):
    match = re.search(r"\b([A-Z]{2,4}\d{3})\b", message, re.I)
    if match:
        return match.group(1)
    else:
        return None

def get_class_info(class_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT class_name, times FROM class_info WHERE class_name LIKE %s"
    cursor.execute(query, ("%"+class_name+"%",))
    result = cursor.fetchone()
    conn.close()

    if result:
        return f"{result[0]} class is scheduled at {result[1]}."
    else:
        return "I couldn't find the class time for {class_name}. Please check the class name and try again."


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
        prompt = f"{anthropic.HUMAN_PROMPT} {system_message}\n\nHuman: {message}\n\nAssistant:"
        response = client.completions.create(
            prompt=prompt,
            model="claude-2.1",
            max_tokens_to_sample=250,
            temperature=0.2,
            stop_sequences=[anthropic.HUMAN_PROMPT],
        )
        response = response.completion

    return response

# Example usage (if needed, but usually this function is called by another part of your application)
if __name__ == "__main__":
    test_message = "When does CS101 class start?"
    print(process_message(test_message))