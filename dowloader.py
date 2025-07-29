import os
import threading
import requests
import mimetypes
from urllib.parse import urlparse
from datetime import datetime
import logging

# === Setup Logging ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/download.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# === File Category Map ===
CATEGORY_MAP = {
    "image": "images",
    "application/pdf": "documents",
    "video": "videos",
}

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def categorize_file(mime_type):
    for key, folder in CATEGORY_MAP.items():
        if mime_type.startswith(key):
            return folder
    return "others"

def get_filename_from_url(url):
    path = urlparse(url).path
    filename = os.path.basename(path)
    return filename or f"file_{threading.get_ident()}"

def download_and_categorize(url):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        mime_type = response.headers.get('Content-Type', '')
        category = categorize_file(mime_type)
        folder_name = os.path.join(DOWNLOAD_DIR, category, datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(folder_name, exist_ok=True)

        filename = get_filename_from_url(url)
        file_path = os.path.join(folder_name, filename)

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        logging.info(f"Downloaded {url} -> {file_path}")
        print(f"[{threading.current_thread().name}] ✅ Downloaded: {filename}")
    except Exception as e:
        logging.error(f"❌ Failed: {url} | Error: {e}")
        print(f"[{threading.current_thread().name}] ❌ Failed to download: {url}")

def main():
    threads = []

    with open("urls.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        t = threading.Thread(target=download_and_categorize, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("\n📦 All downloads completed. Check the logs and folders for details.")

if __name__ == "__main__":
    main()
