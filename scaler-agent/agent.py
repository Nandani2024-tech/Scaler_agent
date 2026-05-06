import os
import json
import time
import re
import sys
from openai import OpenAI
from dotenv import load_dotenv
from tools.file_tools import create_file
from tools.browser_tools import open_in_browser, scrape_website
from tools.asset_tools import download_assets

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENROUTER_API_KEY")
PLANNER_MODEL = "meta-llama/llama-3.1-8b-instruct"
BUILDER_MODEL = "meta-llama/llama-3.1-8b-instruct"

if not OPENROUTER_API_KEY:
    print("\033[91m[ERROR] OpenRouter API Key missing. Please set NVIDIA_API_KEY or OPENROUTER_API_KEY in .env\033[0m")
    sys.exit(1)

# Initialize OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def extract_json(text):
    """Robust JSON extraction from LLM response"""
    if not text: return None
    try:
        # Try direct parsing first
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback to regex extraction
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
    return None

def call_ai(system_prompt, user_prompt, model, is_json=False):
    """OpenRouter caller with exponential backoff for 429s"""
    max_retries = 5
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000,
                response_format={"type": "json_object"} if is_json else None
            )
            
            content = response.choices[0].message.content.strip()
            
            if is_json:
                parsed = extract_json(content)
                if parsed:
                    return parsed
                else:
                    print(f"\033[91m[JSON ERROR] Failed to parse JSON from: {content[:100]}...\033[0m")
                    return content # Return raw content for debugging
            
            return content
            
        except Exception as e:
            if "429" in str(e):
                delay = base_delay * (2 ** attempt)
                print(f"\033[1;33m[RATE LIMIT] 429 Error. Retrying in {delay}s...\033[0m")
                time.sleep(delay)
            else:
                print(f"\033[91m[AI ERROR] {str(e)}\033[0m")
                return None
    return None

def clean_scraped_data(data):
    """Strictly limits data size to prevent overhead and costs"""
    if not data or "error" in data:
        return None
        
    text = data.get("text", "")
    words = text.split()
    limited_text = " ".join(words[:500]) # Reduced to 500 words
    
    headings = data.get("headings", {})
    clean_headings = {k: v[:5] for k, v in headings.items()}
    
    return {
        "url": data.get("url"),
        "title": data.get("title"),
        "headings": clean_headings,
        "buttons": data.get("buttons", [])[:5],
        "text": limited_text,
        "images": data.get("images", [])[:10]
    }

def plan_website(clean_data):
    """[PLANNER] Returns a JSON structure of the website sections"""
    print("\033[1;34m[PLANNER] Creating website structure...\033[0m")
    
    system_prompt = """You are a website architect. Create a structural plan for a website clone.
    OUTPUT RULES:
    - Return ONLY valid JSON.
    - SCHEMA: {"sections": [{"name": "string", "description": "string"}]}
    - Limit to 5-7 essential sections (e.g., Navbar, Hero, Features, Testimonials, Footer)."""
    
    user_prompt = f"""SCRAPED CONTENT:
    TITLE: {clean_data['title']}
    HEADINGS: {json.dumps(clean_data['headings'])}
    BUTTONS: {clean_data['buttons']}
    TEXT SUMMARY: {clean_data['text'][:300]}
    
    Generate a logical section-by-section plan using ONLY this content."""
    
    return call_ai(system_prompt, user_prompt, PLANNER_MODEL, is_json=True)

def build_website(clean_data, plan, asset_map):
    """[BUILDER] Generates HTML, CSS, and JS in a single efficient call"""
    print("\033[1;35m[BUILDER] Generating full website code...\033[0m")
    
    system_prompt = """You are a senior web developer. Generate high-fidelity code for a website.
    STRICT RULES:
    - NO HALLUCINATION. Use ONLY provided text and assets.
    - NO placeholder text like "Lorem Ipsum".
    - If content is missing for a section, skip it.
    - Output MUST be a STRICT JSON object with "html", "css", and "js" keys. No text before or after.
    - HTML must include references to styles.css and script.js.
    - Use modern, responsive CSS (Flexbox/Grid).
    - Image styling: Ensure images are resized properly to fit their containers (object-fit: cover).
    - UI: Avoid oversized elements; keep the layout clean and professional. 
    - Use provided ASSET MAP paths for all images."""
    
    # Escaped curly braces to avoid f-string format errors
    user_prompt = f"""
    PLAN: {json.dumps(plan)}
    CONTENT: {json.dumps(clean_data)}
    ASSET MAP: {json.dumps(asset_map)}
    
    Generate the full static website code (HTML body content, complete CSS, and essential JS).
    Return format: {{"html": "...", "css": "...", "js": "..."}}"""
    
    build_result = call_ai(system_prompt, user_prompt, BUILDER_MODEL, is_json=True)
    
    if not isinstance(build_result, dict):
        print("\033[1;31m[DEBUG] Raw response was not a dictionary:\033[0m", build_result)
        
    return build_result

def run_builder(user_input):
    """Main execution pipeline"""
    url = user_input if user_input.startswith("http") else "https://www.scaler.com"
    print(f"\033[1;36m[START] Cloning website: {url}\033[0m")
    
    # 1. Scrape
    raw_data = scrape_website(url)
    if not raw_data or "error" in raw_data:
        print(f"Agent needs clarification: Could not scrape the website at {url}")
        return

    # 2. Clean
    clean_data = clean_scraped_data(raw_data)
    if not clean_data or not clean_data['text']:
        print("Agent needs clarification: Scraped data is empty or insufficient.")
        return
        
    asset_map = download_assets(clean_data.get("images", []))

    # 3. Plan
    plan = plan_website(clean_data)
    if not plan or not isinstance(plan, dict) or "sections" not in plan:
        print("Agent needs clarification: Designer failed to create a valid plan.")
        return

    # 4. Build
    build_result = build_website(clean_data, plan, asset_map)
    if not build_result or not isinstance(build_result, dict) or not all(k in build_result for k in ["html", "css", "js"]):
        print("Agent needs clarification: Builder failed to generate valid code.")
        return

    # 5. File Generation
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_data['title']}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    {build_result['html']}
    <script src="script.js"></script>
</body>
</html>"""

    create_file("index.html", full_html)
    create_file("styles.css", build_result['css'])
    create_file("script.js", build_result['js'])

    print(f"\033[1;32m[SUCCESS] Website clone ready in 'output/' directory!\033[0m")
    open_in_browser("output/index.html")

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "https://www.scaler.com"
    run_builder(prompt)
