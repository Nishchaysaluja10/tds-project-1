from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Optional
import httpx
import asyncio
from services.github_service import create_github_repo, push_files_to_repo, enable_github_pages, get_github_username, RepoExistsError
from services.openai_service import generate_code_with_openai

# Explicitly load .env from the project's root directory to be more robust
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="TDS Project 1", description="LLM Code Deployment API")

SECRET = os.getenv("SECRET")

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
    except RepoExistsError as e:
        raise HTTPException(status_code=409, detail=f"{e} Please use a different 'nonce' and try again.")
    except Exception as e:
        # It's good practice to log the full error for debugging
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

async def handle_round_one(data: TaskRequest) -> TaskResponse:
    files = await generate_code_with_openai(data.brief, data.task, data.checks)
    repo_name = f"{data.task}_{data.nonce}".replace(" ", "_").lower()

    username = await get_github_username()
    repo_info = await create_github_repo(repo_name)
    await push_files_to_repo(repo_name, files, username)
    await enable_github_pages(repo_name, username)

    pages_url = f"https://{username}.github.io/{repo_name}"

    # Notify the evaluation URL
    eval_payload = {
        "email": data.email,
        "task": data.task,
        "round": data.round,
        "nonce": data.nonce,
        "repo_url": repo_info["html_url"],
        "commit_sha": "main", # Assuming main branch for simplicity
        "pages_url": pages_url,
    }
    await notify_evaluation_url(data.evaluation_url, eval_payload)

    return TaskResponse(
        email=data.email,
        task=data.task,
        round=data.round,
        nonce=data.nonce,
        repo_url=repo_info["html_url"],
        commit_sha="main",
        pages_url=pages_url
    )

async def handle_round_two(data: TaskRequest) -> TaskResponse:
    files = await generate_code_with_openai(f"UPDATE: {data.brief}", data.task, data.checks)
    repo_name = f"{data.task}_{data.nonce}".replace(" ", "_").lower()

    username = await get_github_username()
    await push_files_to_repo(repo_name, files, username)

    pages_url = f"https://{username}.github.io/{repo_name}"
    repo_url = f"https://github.com/{username}/{repo_name}"

    # Notify the evaluation URL
    eval_payload = {
        "email": data.email,
        "task": data.task,
        "round": data.round,
        "nonce": data.nonce,
        "repo_url": repo_url,
        "commit_sha": "main", # Assuming main branch for simplicity
        "pages_url": pages_url,
    }
    await notify_evaluation_url(data.evaluation_url, eval_payload)

    return TaskResponse(
        email=data.email,
        task=data.task,
        round=data.round,
        nonce=data.nonce,
        repo_url=repo_url,
        commit_sha="main",
        pages_url=pages_url
    )

async def notify_evaluation_url(evaluation_url: str, payload: dict):
    """
    Sends a POST request to the evaluation URL with retry logic.
    """
    if not evaluation_url:
        print("No evaluation URL provided. Skipping notification.")
        return

    max_retries = 5
    delay = 1  # Start with a 1-second delay
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(evaluation_url, json=payload, timeout=30)

            if response.status_code == 200:
                print(f"Successfully notified evaluation URL: {evaluation_url}")
                return
            else:
                print(f"Attempt {attempt + 1}/{max_retries}: Failed to notify evaluation URL. Status: {response.status_code}. Retrying...")

        except httpx.RequestError as e:
            print(f"Attempt {attempt + 1}/{max_retries}: An error occurred while notifying evaluation URL: {e}. Retrying...")

        # Exponential backoff
        await asyncio.sleep(delay)
        delay *= 2

    print(f"Failed to notify evaluation URL after {max_retries} attempts.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)