#!/bin/bash

# A script to send a sample task to the running application.
#
# Before running this, make sure you have done two things:
#
# 1. The server is running in another terminal. You can start it with:
#    python -m uvicorn main:app --reload
#
# 2. Your .env file is set up with your secret key. This script
#    assumes the secret is "your-secret-key". If you changed it
#    in your .env file, you must change it here too.

# Use the -s flag for a cleaner output, and -w '\n%{http_code}\n' to print the HTTP status code
curl -s -w "\nHTTP Status Code: %{http_code}\n" -X POST "http://127.0.0.1:8000/handle_task" \
-H "Content-Type: application/json" \
-d '{
  "email": "your-email@example.com",
  "secret": "your-secret-key",
  "task": "simple-portfolio",
  "round": 1,
  "nonce": "project001",
  "brief": "Create a simple, single-page personal portfolio website. It should have my name, a short bio, and a list of my skills. The design should be clean and modern.",
  "checks": [],
  "evaluation_url": "",
  "attachments": []
}'