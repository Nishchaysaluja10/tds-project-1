import os
from openai import AsyncOpenAI
import json
from dotenv import dotenv_values

async def generate_code_with_openai(brief: str, task: str, checks: list) -> dict:
    # Force-read the .env file to bypass any reloading issues
    config = dotenv_values(".env")
    OPENAI_API_KEY = config.get("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set or could not be read from .env file.")

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    checks_list = "\n".join([f"- {c}" for c in checks])

    prompt = f"""
You are an expert web developer tasked with creating a single-page web application based on a detailed brief.
Your goal is to generate two files: `index.html` and `README.md`.

**Project Details:**
*   **Task:** {task}
*   **Brief:** {brief}
*   **Evaluation Checks:** The application will be evaluated against these checks:
{checks_list}

**Instructions:**

1.  **`index.html`:**
    *   Create a complete, self-contained `index.html` file.
    *   All CSS and JavaScript must be embedded within this file.
    *   The application must be fully functional and meet all requirements from the brief and checks.
    *   Ensure the design is clean, modern, and responsive.

2.  **`README.md`:**
    *   Create a professional `README.md` file.
    *   It must include the following sections:
        *   A clear **Summary** of the project's purpose.
        *   A **Setup** section explaining how to run the application (e.g., "Open index.html in a browser").
        *   A **Usage** section explaining how to use the application.
        *   A **Code Explanation** section detailing how the HTML, CSS, and JavaScript work.
        *   A **License** section stating "This project is licensed under the MIT License."

**Output Format:**
You MUST return a single, valid JSON object. Do not include any text or markdown formatting outside of the JSON structure.
The JSON object must have two keys: `index_html` and `readme_md`. The values for these keys must be strings containing the full content of the respective files.

Example of the required JSON output:
```json
{{
  "index_html": "<!DOCTYPE html>\\n<html lang=\\"en\\">\\n<head>...</head>\\n<body>...</body>\\n</html>",
  "readme_md": "# Project Title\\n\\n## Summary\\n..."
}}
```
"""

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert web developer that only responds with JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    response_text = response.choices[0].message.content

    try:
        result = json.loads(response_text)

        if "index_html" not in result or "readme_md" not in result:
            raise ValueError("LLM response is missing required keys.")

        return {
            "index.html": result["index_html"],
            "README.md": result["readme_md"]
        }
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response was: {response_text}")
        return {
            "index.html": "<html><body><h1>Error: Could not generate code.</h1></body></html>",
            "README.md": f"# Error\n\nCould not generate project files. The LLM response was invalid.\n\nRaw response:\n```\n{response_text}\n```"
        }