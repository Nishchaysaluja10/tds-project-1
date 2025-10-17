import requests
import unittest
import os
import multiprocessing
import time
import subprocess

# Set dummy environment variables for testing
os.environ["SECRET"] = "your-secret-key"
os.environ["GITHUB_TOKEN"] = "your-github-personal-access-token"
os.environ["GEMINI_API_KEY"] = "your-gemini-api-key"

class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_process = subprocess.Popen(["python", "run_test_server.py"])
        time.sleep(5)  # Give the server time to start

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()

    def setUp(self):
        self.url = "http://localhost:8001/handle_task"
        self.data = {
            "email": "test@example.com",
            "secret": "your-secret-key",
            "task": "landing_page",
            "round": 1,
            "nonce": "test789",
            "brief": "Create a modern landing page for a tech startup with hero section, features, and contact form. Use gradients and animations.",
            "checks": [],
            "evaluation_url": "",
            "attachments": []
        }

    def test_handle_task_success(self):
        response = requests.post(self.url, json=self.data)

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("pages_url", result)
        print(f"✅ Success! Pages: {result['pages_url']}")

    def test_handle_task_invalid_secret(self):
        self.data["secret"] = "invalid-secret"
        response = requests.post(self.url, json=self.data)
        self.assertEqual(response.status_code, 403)
        print("✅ Successfully tested invalid secret.")

if __name__ == '__main__':
    unittest.main()