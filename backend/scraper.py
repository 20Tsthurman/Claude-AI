import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
import time

# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def scrape_page(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the title
        title_element = soup.find("title")
        title = title_element.text.strip() if title_element else "No title found"

        # Extract the main content
        main_content = ""
        content_elements = soup.select("main p, main ul li, main ol li, main h1, main h2, main h3, main h4, main h5, main h6")
        for element in content_elements:
            main_content += element.get_text(strip=True) + "\n"

        if not main_content:
            main_content = "No main content found"

        logging.info(f"Scraped page: {url} with title: {title}")
        logging.info(f"Content snippet: {main_content[:100]}")

        return title, main_content

    except Exception as e:
        logging.error(f"Error scraping page {url}: {str(e)}")
        return None, None

def scrape_wku_website():
    base_url = "https://www.wku.edu"
    urls_to_scrape = [
        base_url,
        f"{base_url}/about/",
        f"{base_url}/academics/",
        f"{base_url}/undergraduate/course-descriptions/",
        f"{base_url}/registrar/academic_calendars/",
        # Add more URLs as needed
    ]

    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    # Create a table to store the scraped data if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraped_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for url in urls_to_scrape:
        title, main_content = scrape_page(url)

        if title and main_content:
            # Insert the extracted data into the table
            cursor.execute("""
                INSERT INTO scraped_data (url, title, content)
                VALUES (?, ?, ?)
            """, (url, title, main_content))
            logging.info(f"Scraped page: {url}")
        else:
            logging.warning(f"Failed to scrape page: {url}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    while True:
        logging.info("Starting scraper...")
        scrape_wku_website()
        logging.info("Scraping complete. Waiting for the next run.")
        time.sleep(86400)  # Wait for 24 hours (86400 seconds) before the next run