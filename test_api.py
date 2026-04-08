"""
Test the deployed API end-to-end.
"""

import requests
import json
import time

API_URL = "https://zcb2b7rqpf.execute-api.us-east-1.amazonaws.com/prod"

# Test code to review
test_code = """
def calculate(x, y):
    result = x / y
    return result

print(calculate(10, 0))
"""

print("=== Testing CodeSage AI API ===\n")

# Step 1: Submit code
print("1. Submitting code for review...")
response = requests.post(
    f"{API_URL}/submit",
    json={
        "code": test_code,
        "language": "python"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

if response.status_code != 202:
    print("✗ Submission failed!")
    exit(1)

submission_id = response.json()['submission_id']
print(f"✓ Submission ID: {submission_id}\n")

# Step 2: Poll for results
print("2. Waiting for analysis (this may take 30-60 seconds)...")
max_attempts = 20
attempt = 0

while attempt < max_attempts:
    attempt += 1
    print(f"   Attempt {attempt}/{max_attempts}...", end=" ")
    
    response = requests.get(f"{API_URL}/result/{submission_id}")
    result = response.json()
    
    if response.status_code == 200:
        print("✓ Analysis complete!\n")
        print("=== Analysis Result ===")
        print(json.dumps(result, indent=2))
        break
    elif response.status_code == 202:
        print("Still processing...")
        time.sleep(3)
    else:
        print(f"✗ Error: {result}")
        break
else:
    print("\n✗ Timeout waiting for analysis")

print("\n=== Test Complete ===")
