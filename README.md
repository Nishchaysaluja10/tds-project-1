# TDS Project 1: LLM Code Deployment API

This project is a FastAPI application that automates the process of generating and deploying simple web applications using the Google Gemini API and GitHub.

## Features

- **Automated Code Generation:** Leverages the Gemini API to generate HTML, CSS, and JavaScript code based on a given prompt.
- **GitHub Integration:** Automatically creates a new GitHub repository for each generated application.
- **Automated Deployment:** Deploys the generated website to GitHub Pages, making it instantly accessible online.
- **Two-Round Workflow:** Supports an initial creation (Round 1) and a subsequent update (Round 2) of the web application.

## Getting Started

### Prerequisites

- Python 3.7+
- A GitHub account and a personal access token with `repo` permissions.
- A Google Gemini API key.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**

    Create a `.env` file in the root of the project and add the following variables:

    ```
    SECRET="your-secret-key"
    GITHUB_TOKEN="your-github-personal-access-token"
    GEMINI_API_KEY="your-gemini-api-key"
    ```

    - `SECRET`: A secret key to authorize requests to your API.
    - `GITHUB_TOKEN`: Your GitHub personal access token.
    - `GEMINI_API_KEY`: Your API key for the Gemini service.

### Running the Application

To start the FastAPI server, run the following command:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Usage

You can interact with the API by sending POST requests to the `/handle_task` endpoint.

### Request Body

- `email` (str): Your email address.
- `secret` (str): The secret key you defined in your `.env` file.
- `task` (str): A short name for the task (e.g., "Landing Page").
- `round` (int): The task round (1 for creation, 2 for update).
- `nonce` (str): A unique identifier for the task.
- `brief` (str): A detailed description of the web application you want to create or update.
- `attachments` (list): A list of dictionaries, each representing a file to be used in the task.
- `checks` (list): A list of JavaScript expressions that the generated code must pass.

### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/handle_task" -H "Content-Type: application/json" -d '{
  "email": "test@example.com",
  "secret": "your-secret-key",
  "task": "Simple Calculator",
  "round": 1,
  "nonce": "abc123",
  "brief": "Create a simple calculator with basic arithmetic operations."
}'
```

### Response Body

The API will respond with a JSON object containing the URLs for the new GitHub repository and the deployed GitHub Pages site.

- `email` (str): Your email address.
- `task` (str): The name of the task.
- `round` (int): The task round.
- `nonce` (str): The unique identifier for the task.
- `repo_url` (str): The URL of the created GitHub repository.
- `commit_sha` (str): The commit SHA of the deployed code.
- `pages_url` (str): The URL of the live application on GitHub Pages.