from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import base64
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()

app = FastAPI(title="TDS Project 1", description="LLM Code Deployment API")

SECRET = os.getenv("SECRET")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
AIPIPE_API_KEY = os.getenv("AIPIPE_API_KEY")
AIPIPE_BASE_URL = "https://aipipe.org/openai/v1"

class TaskRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: Optional[List[str]] = []
    evaluation_url: Optional[str] = ""
    attachments: Optional[List[dict]] = []

class TaskResponse(BaseModel):
    email: str
    task: str
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str

@app.get("/")
async def health_check():
    return {"status": "TDS Project 1 API is running", "version": "1.0.0"}

@app.post("/handle_task", response_model=TaskResponse)
async def handle_task(data: TaskRequest):
    if data.secret != SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    try:
        if data.round == 1:
            return await handle_round_one(data)
        elif data.round == 2:
            return await handle_round_two(data)
        else:
            raise HTTPException(status_code=400, detail="Invalid round")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Helper Logic Below -----------------

async def handle_round_one(data: TaskRequest) -> TaskResponse:
    files = await generate_code_with_aipipe(data.brief, data.task)
    repo_name = f"{data.task}_{data.nonce}".replace(" ", "_").lower()
    repo_info = create_github_repo(repo_name)
    push_files_to_repo(repo_name, files)
    enable_github_pages(repo_name)
    return TaskResponse(
        email=data.email,
        task=data.task,
        round=data.round,
        nonce=data.nonce,
        repo_url=repo_info["html_url"],
        commit_sha="main",
        pages_url=f"https://{get_github_username()}.github.io/{repo_name}"
    )

async def handle_round_two(data: TaskRequest) -> TaskResponse:
    files = await generate_code_with_aipipe(f"UPDATE: {data.brief}", data.task)
    repo_name = f"{data.task}_{data.nonce}".replace(" ", "_").lower()
    push_files_to_repo(repo_name, files)
    return TaskResponse(
        email=data.email,
        task=data.task,
        round=data.round,
        nonce=data.nonce,
        repo_url=f"https://github.com/{get_github_username()}/{repo_name}",
        commit_sha="main",
        pages_url=f"https://{get_github_username()}.github.io/{repo_name}"
    )

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
    if "```
        html_code = html_code.split("```html").split("```
    elif "```" in html_code:
        parts = html_code.split("```
        if len(parts) >= 3:
            html_code = parts.strip()[1]
    return {
        "index.html": html_code,
        "README.md": f"# {task}\n\n{brief}\n\nOpen index.html to use the application."
    }

def get_github_username():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    return response.json()["login"]

def create_github_repo(repo_name: str) -> dict:
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {
        "name": repo_name,
        "private": False,
        "auto_init": True,
        "license_template": "mit"
    }
    response = requests.post("https://api.github.com/user/repos", headers=headers, json=payload)
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Repo creation failed: {response.status_code}, {response.text}")

def push_files_to_repo(repo_name: str, files: dict):
    username = get_github_username()
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    for filename, content in files.items():
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
        url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{filename}"
        existing = requests.get(url, headers=headers)
        payload = {"message": f"Add {filename}", "content": content_b64}
        if existing.status_code == 200:
            payload["sha"] = existing.json()["sha"]
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code not in :
            raise Exception(f"Failed to push {filename}: {response.status_code}, {response.text}")

def enable_github_pages(repo_name: str):
    username = get_github_username()
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"source": {"branch": "main", "path": "/"}}
    requests.post(
        f"https://api.github.com/repos/{username}/{repo_name}/pages",
        headers=headers, json=payload
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
