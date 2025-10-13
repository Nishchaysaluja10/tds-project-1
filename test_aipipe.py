import requests

def test_api():
    url = "http://localhost:8000/handle_task"
    data = {
        "email": "test@example.com",
        "secret": "messi10",  # Your secret
        "task": "landing_page",
        "round": 1,
        "nonce": "test789",
        "brief": "Create a modern landing page for a tech startup with hero section, features, and contact form. Use gradients and animations.",
        "checks": [],
        "evaluation_url": "",
        "attachments": []
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Pages: {result['pages_url']}")
    else:
        print(f"❌ Failed: {response.text}")

test_api()
