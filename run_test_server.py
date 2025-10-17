import uvicorn
from unittest.mock import patch, MagicMock

@patch('main.generate_code_with_gemini')
@patch('main.get_github_username')
@patch('main.create_github_repo')
@patch('main.push_files_to_repo')
@patch('main.enable_github_pages')
def run_server(mock_enable_pages, mock_push_files, mock_create_repo, mock_get_username, mock_generate_code):
    # Configure the mocks to return successful responses
    mock_generate_code.return_value = {
        "index.html": "<html><body><h1>Test</h1></body></html>",
        "README.md": "# Test"
    }
    mock_get_username.return_value = "testuser"
    mock_create_repo.return_value = {"html_url": "https://github.com/testuser/test_repo"}
    mock_push_files.return_value = None
    mock_enable_pages.return_value = None
    uvicorn.run("main:app", host="0.0.0.0", port=8001, log_level="info")

if __name__ == "__main__":
    run_server()