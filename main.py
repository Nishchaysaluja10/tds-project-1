from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import List, Optional
from services.github_service import create_github_repo, push_files_to_repo, enable_github_pages, get_github_username, RepoExistsError
from services.gemini_service import generate_code_with_gemini

load_dotenv()

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
    files = await generate_code_with_gemini(data.brief, data.task)
    repo_name = f"{data.task}_{data.nonce}".replace(" ", "_").lower()

    username = await get_github_username()
    repo_info = await create_github_repo(repo_name)
    await push_files_to_repo(repo_name, files, username)
    await enable_github_pages(repo_name, username)

    return TaskResponse(
        email=data.email,
        task=data.task,
        round=data.round,
        nonce=data.nonce,
        repo_url=repo_info["html_url"],
        commit_sha="main",
        pages_url=f"https://{username}.github.io/{repo_name}"
    )

async def handle_round_two(data: TaskRequest) -> TaskResponse:
    files = await generate_code_with_gemini(f"UPDATE: {data.brief}", data.task)
    repo_name = f"{data.task}_{data.nonce}".replace(" ", "_").lower()

    username = await get_github_username()
    await push_files_to_repo(repo_name, files, username)

    return TaskResponse(
        email=data.email,
        task=data.task,
        round=data.round,
        nonce=data.nonce,
        repo_url=f"https://github.com/{username}/{repo_name}",
        commit_sha="main",
        pages_url=f"https://{username}.github.io/{repo_name}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)