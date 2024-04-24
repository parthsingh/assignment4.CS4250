import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urljoin

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["cs_website"]
pages_collection = db["pages"]

def retrieve_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to retrieve HTML from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error retrieving HTML from {url}: {e}")
        return None

def store_page(url, html):
    if html:
        try:
            pages_collection.insert_one({"url": url, "html": html})
            print(f"Page stored: {url}")
        except Exception as e:
            print(f"Error storing page {url} in MongoDB: {e}")

def parse_html(html):
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all('a', href=True)
    else:
        return []

def target_page(html):
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            if heading.text.strip().lower() == "permanent faculty":
                return True
    return False

def crawler_thread(frontier):
    while frontier:
        url = frontier.pop(0)
        html = retrieve_html(url)
        if html:
            store_page(url, html)
            if target_page(html):
                print("Target page found!")
                break
            else:
                links = parse_html(html)
                for link in links:
                    next_url = urljoin(url, link['href'])
                    frontier.append(next_url)

if __name__ == "__main__":
    frontier = ["https://www.cpp.edu/sci/computer-science/"]
    crawler_thread(frontier)
