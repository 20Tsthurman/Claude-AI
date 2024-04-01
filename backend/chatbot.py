import sqlite3
import time
import anthropic
from config import API_KEY

client = anthropic.Anthropic(api_key=API_KEY)

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

    keywords = ["about", "academics", "courses", "calendar"]
    relevant_keyword = next((keyword for keyword in keywords if keyword in message.lower()), None)

    if relevant_keyword:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()

        retry_count = 3
        result = None  # Initialize result to None
        while retry_count > 0:
            try:
                # Retrieve the relevant scraped data for the keyword found in the message
                query = "SELECT title, content FROM scraped_data WHERE url LIKE ? ORDER BY timestamp DESC LIMIT 1"
                cursor.execute(query, (f"%{relevant_keyword}%",))
                result = cursor.fetchone()
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    retry_count -= 1
                    time.sleep(1)  # Wait for 1 second before retrying
                else:
                    print(f"Database error: {e}")
                    break

        conn.close()

        if result:
            title, content = result
            response = f"Here's the relevant information from the WKU website:\nTitle: {title}\nContent: {content}"
        else:
            response = "Sorry, I couldn't find any relevant information from the WKU website for your query."
    else:
        # Process the message using Claude 2.1
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