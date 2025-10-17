import requests
import unittest
import os
import time
import subprocess
import base64

# Set dummy environment variables for testing
os.environ["SECRET"] = "your-secret-key"
os.environ["GITHUB_TOKEN"] = "your-github-personal-access-token"
os.environ["GEMINI_API_KEY"] = "your-gemini-api-key"

class TestApi(unittest.TestCase):
    server_process = None

    @classmethod
    def setUpClass(cls):
        # Start the mocked server as a subprocess
        cls.server_process = subprocess.Popen(["python", "run_test_server.py"])
        time.sleep(5)  # Give the server time to start up

    @classmethod
    def tearDownClass(cls):
        # Terminate the server process
        cls.server_process.terminate()

    def setUp(self):
        self.base_url = "http://localhost:8001"
        self.task_url = f"{self.base_url}/handle_task"

        # Sample data for a Round 1 task
        csv_content = "product,sales\nLaptop,1500\nMouse,100"
        csv_base64 = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')

        self.round1_data = {
            "email": "test@example.com",
            "secret": "your-secret-key",
            "task": "sum-of-sales",
            "round": 1,
            "nonce": "test12345",
            "brief": "Publish a single-page site that fetches data.csv from attachments, sums its sales column, and displays the total inside #total-sales.",
            "checks": [
                "js: document.title === 'Sales Summary'",
                "js: !!document.querySelector('#total-sales')"
            ],
            "evaluation_url": "http://localhost:8001/evaluate", # Mock evaluation endpoint
            "attachments": [
                {
                    "name": "data.csv",
                    "url": f"data:text/csv;base64,{csv_base64}"
                }
            ]
        }

        # Sample data for a Round 2 task
        self.round2_data = self.round1_data.copy()
        self.round2_data["round"] = 2
        self.round2_data["brief"] = "Update the site to also display the average sales in an element with id #average-sales."

    def test_01_health_check(self):
        """Test if the server is running."""
        response = requests.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], "TDS Project 1 API is running")
        print("✅ Health check passed.")

    def test_02_handle_task_round1_success(self):
        """Test a successful Round 1 task submission."""
        response = requests.post(self.task_url, json=self.round1_data)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("pages_url", result)
        self.assertEqual(result['task'], 'sum-of-sales')
        print(f"✅ Round 1 success! Pages URL: {result['pages_url']}")

    def test_03_handle_task_round2_success(self):
        """Test a successful Round 2 task submission."""
        response = requests.post(self.task_url, json=self.round2_data)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("pages_url", result)
        self.assertEqual(result['round'], 2)
        print(f"✅ Round 2 success! Pages URL: {result['pages_url']}")

    def test_04_handle_task_invalid_secret(self):
        """Test the API's response to an invalid secret."""
        invalid_data = self.round1_data.copy()
        invalid_data["secret"] = "wrong-secret"
        response = requests.post(self.task_url, json=invalid_data)
        self.assertEqual(response.status_code, 403)
        print("✅ Successfully tested invalid secret.")

if __name__ == '__main__':
    unittest.main()