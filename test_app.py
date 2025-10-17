import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import os
import base64

# Set dummy environment variables before importing the app
os.environ["SECRET"] = "your-secret-key"
os.environ["GITHUB_TOKEN"] = "dummy-github-token"
os.environ["AIPIPE_API_KEY"] = "dummy-aipipe-key"

# Import the app instance from main
from main import app

class TestApi(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.task_url = "/handle_task"

        csv_content = "product,sales\nLaptop,1500\nMouse,100"
        csv_base64 = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')

        self.round1_data = {
            "email": "test@example.com",
            "secret": "your-secret-key",
            "task": "sum-of-sales",
            "round": 1,
            "nonce": "test12345",
            "brief": "Generate a site that sums sales.",
            "attachments": [{"name": "data.csv", "url": f"data:text/csv;base64,{csv_base64}"}]
        }

        self.round2_data = {**self.round1_data, "round": 2, "brief": "Update the site for average sales."}

    def test_01_health_check(self):
        """Test if the server is running."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("API is running", response.json()['status'])
        print("✅ Health check passed.")

    @patch('main.handle_round_one', new_callable=AsyncMock)
    def test_02_handle_task_round1_success(self, mock_handle_round_one):
        """Test a successful Round 1 task submission with a mocked handler."""
        # This dictionary must match the TaskResponse Pydantic model
        mock_return_value = {
            "email": self.round1_data['email'],
            "task": self.round1_data['task'],
            "round": self.round1_data['round'],
            "nonce": self.round1_data['nonce'],
            "repo_url": "https://github.com/test/test-repo",
            "commit_sha": "dummy_sha",
            "pages_url": "https://test.github.io/test-repo"
        }
        mock_handle_round_one.return_value = mock_return_value

        response = self.client.post(self.task_url, json=self.round1_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_return_value)
        # The mock was called, which is confirmed by the successful response.
        print("✅ Round 1 success (mocked)!")

    @patch('main.handle_round_two', new_callable=AsyncMock)
    def test_03_handle_task_round2_success(self, mock_handle_round_two):
        """Test a successful Round 2 task submission with a mocked handler."""
        mock_return_value = {
            "email": self.round2_data['email'],
            "task": self.round2_data['task'],
            "round": self.round2_data['round'],
            "nonce": self.round2_data['nonce'],
            "repo_url": "https://github.com/test/test-repo",
            "commit_sha": "dummy_sha_2",
            "pages_url": "https://test.github.io/test-repo"
        }
        mock_handle_round_two.return_value = mock_return_value

        response = self.client.post(self.task_url, json=self.round2_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_return_value)
        # The mock was called, which is confirmed by the successful response.
        print("✅ Round 2 success (mocked)!")

    def test_04_handle_task_invalid_secret(self):
        """Test the API's response to an invalid secret."""
        invalid_data = self.round1_data.copy()
        invalid_data["secret"] = "wrong-secret"
        response = self.client.post(self.task_url, json=invalid_data)
        self.assertEqual(response.status_code, 403)
        print("✅ Successfully tested invalid secret.")

if __name__ == '__main__':
    unittest.main()