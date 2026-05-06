import os
import requests
from urllib.parse import urlparse

def download_assets(image_urls, output_dir="output/assets"):
    """
    Downloads images locally and returns a mapping of original_url -> local_path
    """
    print(f"\033[1;30m[TOOL] Downloading {len(image_urls)} assets...\033[0m")
    os.makedirs(output_dir, exist_ok=True)
    mapping = {}
    
    for i, url in enumerate(image_urls):
        try:
            # Generate a safe filename
            ext = os.path.splitext(urlparse(url).path)[1]
            if not ext: ext = ".jpg"
            filename = f"asset_{i}{ext}"
            filepath = os.path.join(output_dir, filename)
            
            # Simple check if already exists or invalid url
            if not url.startswith("http"): continue
            
            response = requests.get(url, timeout=5, stream=True)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                mapping[url] = f"assets/{filename}"
                if i >= 10: break # Safety limit
        except:
            continue
            
    return mapping
