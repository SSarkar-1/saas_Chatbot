import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

BASE_URL = "https://stripe.com/docs"
HEADERS = {"User-Agent": "Mozilla/5.0"}

visited = set()
MAX_PAGES = 20

os.makedirs("data", exist_ok=True)


def extract_main_content(soup):
    """
    Extract only main article content.
    """
    main = soup.find("main")

    if not main:
        main = soup.find("article")

    if not main:
        main = soup.body

    text = main.get_text("\n", strip=True)

    return text


def save_page(url, text):

    filename = urlparse(url).path.replace("/", "_")

    if filename == "":
        filename = "home"

    with open(f"data/{filename}.txt", "w", encoding="utf-8") as f:
        f.write(text)


def crawl(url):

    if url in visited:
        return

    if not url.startswith(BASE_URL):
        return

    if len(visited) >= MAX_PAGES:
        return

    print("Crawling:", url)

    visited.add(url)

    try:
        time.sleep(1)

        r = requests.get(url, headers=HEADERS, timeout=20)

        soup = BeautifulSoup(r.text, "html.parser")

        text = extract_main_content(soup)

        save_page(url, text)

        for link in soup.find_all("a", href=True):

            next_url = urljoin(url, link["href"])

            parsed = urlparse(next_url)

            clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path

            if clean_url.startswith(BASE_URL):

                crawl(clean_url)

    except Exception as e:
        print("Error:", e)


crawl(BASE_URL)

print("Total pages crawled:", len(visited))