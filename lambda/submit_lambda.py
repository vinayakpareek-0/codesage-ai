"""
Submit Lambda Function

This Lambda function handles code submissions from API Gateway.
It validates input, stores code in S3, and returns a submission ID.
"""

import json
import uuid
import boto3
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')

# Configuration
BUCKET_NAME = 'ai-code-reviewer-vinayak'    
SUPPORTED_LANGUAGES = ['python', 'javascript', 'java', 'go', 'typescript']

def handler(event, context):
    """
    Lambda handler function - AWS calls this when the Lambda is invoked.
    
    Args:
        event: Contains the API Gateway request data (body, headers, etc.)
        context: AWS Lambda runtime information (not used here)
    
    Returns:
        Dictionary with statusCode and body (API Gateway format)
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # Parse the request body
    # API Gateway sends the body as a JSON string, so we parse it
    try:
        body = json.loads(event['body'])
    except (KeyError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'BadRequest',
                'message': 'Invalid JSON in request body'
            })
        }
    
    # Generate a unique submission ID
    submission_id = str(uuid.uuid4())
    
    # Return success response
    return {
        'statusCode': 202,  # 202 = Accepted (processing will happen async)
        'body': json.dumps({
            'submission_id': submission_id,
            'status': 'processing',
            'message': 'Code submitted for review'
        })
    }
