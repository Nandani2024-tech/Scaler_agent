import requests
import webbrowser
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def scrape_website(url: str) -> dict:
    """
    Scrapes a website and returns structured data (HTML, text, links, images, etc.)
    """
    print(f"\033[1;30m[TOOL] Scraping: {url}...\033[0m")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements from text extraction
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        data = {
            "url": url,
            "html": str(soup),
            "title": soup.title.string if soup.title else "No Title",
            "text": soup.get_text(separator=' ', strip=True),
            "links": [urljoin(url, a.get('href')) for a in soup.find_all('a', href=True)][:50],
            "images": [urljoin(url, img.get('src')) for img in soup.find_all('img', src=True)][:30],
            "headings": {
                f"h{i}": [h.get_text(strip=True) for h in soup.find_all(f"h{i}")]
                for i in range(1, 4)
            },
            "buttons": [b.get_text(strip=True) for b in soup.find_all(['button', 'a'], class_=lambda x: x and 'btn' in x.lower())]
        }
        
        return data
    except Exception as e:
        print(f"\033[91m[SCRAPE ERROR] {str(e)}\033[0m")
        return {"error": str(e)}

def extract_styles(url: str) -> str:
    """
    Attempts to fetch CSS from the URL.
    """
    print(f"\033[1;30m[TOOL] Extracting styles from: {url}...\033[0m")
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        css_links = [urljoin(url, link.get('href')) for link in soup.find_all('link', rel='stylesheet')]
        
        combined_css = ""
        for link in css_links[:3]: # Limit to first 3 for speed
            try:
                css_res = requests.get(link, timeout=5)
                combined_css += f"\n/* Source: {link} */\n" + css_res.text + "\n"
            except:
                continue
        return combined_css
    except:
        return ""

def open_in_browser(file_path: str) -> str:
    """Opens the given HTML file in the default web browser."""
    try:
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return f"Error: File {file_path} does not exist at {abs_path}"
        
        # In some environments, webbrowser needs file:// prefix for local files
        url = "file://" + abs_path
        webbrowser.open(url)
        return f"Successfully opened {file_path} in browser."
    except Exception as e:
        return f"Error opening {file_path} in browser: {str(e)}"
