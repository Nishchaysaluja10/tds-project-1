import os
import google.generativeai as genai
import json
from dotenv import dotenv_values
import base64

async def generate_code_with_gemini(brief: str, task: str, checks: list, attachments: list, existing_code: str = None) -> dict:
    config = dotenv_values(".env")
    GEMINI_API_KEY = config.get("GEMINI_API_KEY")

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set or could not be read from .env file.")

    genai.configure(api_key=GEMINI_API_KEY)

    # Prepare the attachments content for the prompt
    attachments_content = ""
    if attachments:
        attachments_content += "\n\n**Attachments:**\n"
        for attachment in attachments:
            try:
                # Assuming the attachment URL is a data URI
                header, encoded = attachment['url'].split(",", 1)
                decoded_content = base64.b64decode(encoded).decode('utf-8')
                attachments_content += f"--- {attachment['name']} ---\n"
                attachments_content += f"```{decoded_content}```\n"
            except Exception as e:
                print(f"Could not decode attachment {attachment['name']}: {e}")
                attachments_content += f"--- {attachment['name']} ---\n[Could not decode content]\n"

    # Prepare the checks content for the prompt
    checks_list = "\n".join([f"- `{c}`" for c in checks]) if checks else "No specific checks provided."

    # Prepare the prompt based on whether it's a new creation or a modification
    if existing_code:
        # This is a Round 2 modification
        prompt = f"""
You are an expert web developer modifying an existing single-page web application.
Your goal is to update the `index.html` file based on a new brief, while ensuring all new and old requirements are met.

**Original Code (`index.html`):**
```html
{existing_code}
```

**New Brief for Modification:**
*   **Task:** {task}
*   **Instructions:** {brief}

**Mandatory Evaluation Checks:**
The final code MUST pass these JavaScript-based checks. Ensure your script logic fulfills every single one.
{checks_list}
{attachments_content}

**Instructions:**

1.  **Modify `index.html`:**
    *   Update the provided `index.html` to implement the new features from the brief.
    *   Ensure the final code is a complete, self-contained HTML file with all CSS and JavaScript embedded.
    *   The final application must pass all evaluation checks.

**Output Format:**
You MUST return a single, valid JSON object with one key: `index_html`. The value must be a string containing the full, updated content of the file.
Example:
```json
{{
  "index_html": "<!DOCTYPE html>\\n<html lang=\\"en\\">...</html>"
}}
```
"""
    else:
        # This is a Round 1 creation
        prompt = f"""
You are an expert web developer creating a single-page web application from scratch.
Your goal is to generate two files: `index.html` and `README.md`.

**Project Details:**
*   **Task:** {task}
*   **Brief:** {brief}

**Mandatory Evaluation Checks:**
The code you write MUST pass these JavaScript-based checks. Ensure your script logic fulfills every single one.
{checks_list}
{attachments_content}

**Instructions:**

1.  **`index.html`:**
    *   Create a complete, self-contained `index.html` file with all CSS and JavaScript embedded.
    *   The application must be fully functional and meet all requirements from the brief and checks.
    *   Ensure the design is clean, modern, and responsive.

2.  **`README.md`:**
    *   Create a professional `README.md` file. It must include:
        *   A clear **Summary** of the project.
        *   A **Setup** section (e.g., "Open index.html in a browser").
        *   A **Usage** section explaining how to use the application.
        *   A **Code Explanation** section detailing how the code works.
        *   A **License** section stating "This project is licensed under the MIT License."

**Output Format:**
You MUST return a single, valid JSON object with two keys: `index_html` and `readme_md`. The values must be strings containing the full content of the respective files.
Example:
```json
{{
  "index_html": "<!DOCTYPE html>...</html>",
  "readme_md": "# Project Title\\n..."
}}
```
"""

    model = genai.GenerativeModel('gemini-1.0-pro')
    response = await model.generate_content_async(prompt)
    response_text = response.text

    try:
        if response_text.startswith("```json"):
            response_text = response_text[7:-4].strip()
        result = json.loads(response_text)

        if existing_code:
            if "index_html" not in result:
                raise ValueError("LLM response for Round 2 is missing 'index_html' key.")
            return {"index.html": result["index_html"]}
        else:
            if "index_html" not in result or "readme_md" not in result:
                raise ValueError("LLM response for Round 1 is missing required keys.")
            return {
                "index.html": result["index_html"],
                "README.md": result["readme_md"]
            }
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response was: {response_text}")
        # Provide a fallback error response
        error_html = "<html><body><h1>Error: Could not generate code due to an invalid response from the AI.</h1></body></html>"
        error_readme = f"# Error\n\nCould not generate project files. The LLM response was invalid.\n\n**Raw Response:**\n```\n{response_text}\n```"
        if existing_code:
            return {"index.html": error_html}
        else:
            return {"index.html": error_html, "README.md": error_readme}