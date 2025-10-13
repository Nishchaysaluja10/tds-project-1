import httpx
import base64
import os

class RepoExistsError(Exception):
    """Custom exception for when a repository already exists."""
    pass

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

async def get_github_username():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/user", headers=headers)
    response.raise_for_status()
    return response.json()["login"]

async def create_github_repo(repo_name: str) -> dict:
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {
        "name": repo_name,
        "private": False,
        "auto_init": True,
        "license_template": "mit"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.github.com/user/repos", headers=headers, json=payload)

    if response.status_code == 201:
        return response.json()
    elif response.status_code == 422:
        raise RepoExistsError(f"Repository '{repo_name}' already exists.")
    else:
        response.raise_for_status()

async def push_files_to_repo(repo_name: str, files: dict, username: str):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    async with httpx.AsyncClient() as client:
        for filename, content in files.items():
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
            url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{filename}"

            # Check if file exists to get its SHA
            get_response = await client.get(url, headers=headers)
            sha = None
            if get_response.status_code == 200:
                sha = get_response.json()["sha"]

            payload = {"message": f"Add {filename}", "content": content_b64}
            if sha:
                payload["sha"] = sha

            put_response = await client.put(url, headers=headers, json=payload)
            if put_response.status_code not in [200, 201]:
                raise Exception(f"Failed to push {filename}: {put_response.status_code}, {put_response.text}")

async def enable_github_pages(repo_name: str, username: str):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"source": {"branch": "main", "path": "/"}}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{username}/{repo_name}/pages",
            headers=headers, json=payload
        )
    response.raise_for_status()