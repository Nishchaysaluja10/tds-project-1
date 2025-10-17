import uvicorn
from unittest.mock import patch, MagicMock

@patch('main.generate_code_with_gemini')
@patch('main.get_github_username')
@patch('main.create_github_repo')
@patch('main.push_files_to_repo')
@patch('main.enable_github_pages')
@patch('main.get_file_content')
def run_server(mock_get_file_content, mock_enable_pages, mock_push_files, mock_create_repo, mock_get_username, mock_generate_code):
    # --- Mock configurations ---

    # Mock for get_github_username
    mock_get_username.return_value = "testuser"

    # Mock for create_github_repo
    mock_create_repo.return_value = {"html_url": "https://github.com/testuser/test_repo"}

    # Mock for push_files_to_repo
    mock_push_files.return_value = None

    # Mock for enable_github_pages
    mock_enable_pages.return_value = None

    # Mock for get_file_content (for Round 2)
    mock_get_file_content.return_value = "<html><body><h1>Original Content</h1></body></html>"

    # Mock for generate_code_with_gemini
    # This mock can be simple because we're testing the wiring, not the AI
    def mock_gemini_logic(brief, task, checks, attachments, existing_code=None):
        if existing_code:
            # Round 2 response
            return {"index.html": "<html><body><h1>Updated Content</h1></body></html>"}
        else:
            # Round 1 response
            return {
                "index.html": "<html><body><h1>Test Page</h1></body></html>",
                "README.md": "# Test Readme"
            }
    mock_generate_code.side_effect = mock_gemini_logic

    # --- Run the server ---
    uvicorn.run("main:app", host="0.0.0.0", port=8001, log_level="info")

if __name__ == "__main__":
    run_server()