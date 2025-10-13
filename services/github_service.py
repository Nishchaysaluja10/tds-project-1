import requests
import base64
import os

class RepoExistsError(Exception):
    """Custom exception for when a repository already exists."""
    pass

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_github_username():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    response.raise_for_status()
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
    elif response.status_code == 422:
        # This status code is often returned if the repo already exists
        raise RepoExistsError(f"Repository '{repo_name}' already exists.")
    else:
        response.raise_for_status() # Raise an exception for other bad responses (4xx or 5xx)

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
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to push {filename}: {response.status_code}, {response.text}")

def enable_github_pages(repo_name: str):
    username = get_github_username()
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"source": {"branch": "main", "path": "/"}}
    response = requests.post(
        f"https://api.github.com/repos/{username}/{repo_name}/pages",
        headers=headers, json=payload
    )
    response.raise_for_status()