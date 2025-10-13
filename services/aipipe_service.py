import requests
import os
import re

AIPIPE_API_KEY = os.getenv("AIPIPE_API_KEY")
AIPIPE_BASE_URL = "https://aipipe.org/openai/v1"

async def generate_code_with_aipipe(brief: str, task: str) -> dict:
    prompt = f"""Create a complete web application:

Task: {task}
Brief: {brief}

Requirements:
1. Single HTML file with embedded CSS and JavaScript
2. Responsive and modern design
3. All functionality from the brief
4. No external dependencies

Return ONLY the HTML code."""
    headers = {
        "Authorization": f"Bearer {AIPIPE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an expert web developer."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 3500,
        "temperature": 0.3
    }
    response = requests.post(
        f"{AIPIPE_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    if response.status_code != 200:
        raise Exception(f"AIPipe API error: {response.status_code}: {response.text}")

    result = response.json()
    html_code = result["choices"][0]["message"]["content"].strip()

    # Corrected Markdown cleanup using regex
    match = re.search(r"```html\n(.*?)\n```", html_code, re.DOTALL)
    if match:
        html_code = match.group(1).strip()
    elif html_code.startswith("```") and html_code.endswith("```"):
        html_code = html_code[3:-3].strip()

    return {
        "index.html": html_code,
        "README.md": f"# {task}\n\n{brief}\n\nOpen index.html to use the application."
    }