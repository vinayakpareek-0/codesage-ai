"""
Local test script for Submit Lambda function.
"""

import json
import sys
sys.path.insert(0, 'lambda')

from submit_lambda import handler

# Test 1: Valid submission
print("Test 1: Valid submission")
event = {
    'body': json.dumps({
        'code': 'def hello():\n    print("Hello")',
        'language': 'python'
    })
}
response = handler(event, None)
print(f"Status: {response['statusCode']}, Body: {response['body']}\n")

# Test 2: Missing code field
print("Test 2: Missing code field")
event = {'body': json.dumps({'language': 'python'})}
response = handler(event, None)
print(f"Status: {response['statusCode']}, Body: {response['body']}\n")

# Test 3: Code too large
print("Test 3: Code too large")
event = {'body': json.dumps({'code': 'x=1\n' * 20000, 'language': 'python'})}
response = handler(event, None)
print(f"Status: {response['statusCode']}, Body: {response['body']}\n")

print("✓ Tests complete")
