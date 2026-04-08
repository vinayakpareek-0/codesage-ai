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
lambda_client = boto3.client('lambda')

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
    
    # Validate input
    validation_error = validate_input(body)
    if validation_error:
        return validation_error
    
    # Generate a unique submission ID
    submission_id = str(uuid.uuid4())
    
    # Store code in S3
    storage_error = store_code_in_s3(submission_id, body['code'], body['language'])
    if storage_error:
        return storage_error
    
    # Trigger Analyze Lambda asynchronously
    trigger_analyze_lambda(submission_id, body['language'])
    
    # Return success response
    return {
        'statusCode': 202,  # 202 = Accepted (processing will happen async)
        'body': json.dumps({
            'submission_id': submission_id,
            'status': 'processing',
            'message': 'Code submitted for review'
        })
    }


def validate_input(body):
    """
    Validate the request body contains required fields and meets constraints.
    
    Args:
        body: Parsed JSON body from the request
    
    Returns:
        Error response dict if validation fails, None if valid
    """
    
    # Check for required field: code
    if 'code' not in body:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'BadRequest',
                'message': 'Missing required field: code'
            })
        }
    
    # Check for required field: language
    if 'language' not in body:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'BadRequest',
                'message': 'Missing required field: language'
            })
        }
    
    code = body['code']
    language = body['language']
    
    # Validate code is not empty
    if not code or not isinstance(code, str):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'BadRequest',
                'message': 'Field "code" must be a non-empty string'
            })
        }
    
    # Check code size limit (100KB = 102400 bytes)
    code_size = len(code.encode('utf-8'))
    if code_size > 102400:
        return {
            'statusCode': 413,
            'body': json.dumps({
                'error': 'PayloadTooLarge',
                'message': f'Code content exceeds maximum size of 100KB (received {code_size} bytes)'
            })
        }
    
    # Validate language is supported
    if language not in SUPPORTED_LANGUAGES:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'BadRequest',
                'message': f'Unsupported language: {language}. Supported languages: {", ".join(SUPPORTED_LANGUAGES)}'
            })
        }
    
    # All validations passed
    return None


def get_file_extension(language):
    """Get file extension for a programming language."""
    extensions = {
        'python': 'py',
        'javascript': 'js',
        'java': 'java',
        'go': 'go',
        'typescript': 'ts'
    }
    return extensions.get(language, 'txt')


def store_code_in_s3(submission_id, code, language):
    """
    Store code in S3 bucket with metadata.
    
    Args:
        submission_id: Unique identifier for this submission
        code: Source code content
        language: Programming language
    
    Returns:
        Error response dict if storage fails, None if successful
    """
    
    try:
        # Get file extension
        extension = get_file_extension(language)
        
        # Create S3 key (path)
        s3_key = f'submissions/{submission_id}/code.{extension}'
        
        # Store in S3 with metadata
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=code.encode('utf-8'),
            Metadata={
                'language': language,
                'submitted_at': datetime.utcnow().isoformat(),
                'size_bytes': str(len(code.encode('utf-8')))
            }
        )
        
        print(f"Code stored successfully: {s3_key}")
        return None
        
    except Exception as e:
        print(f"Error storing code in S3: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'InternalServerError',
                'message': 'Failed to store code submission. Please try again later.'
            })
        }


def trigger_analyze_lambda(submission_id, language):
    """
    Trigger Analyze Lambda asynchronously.
    
    Args:
        submission_id: Submission identifier
        language: Programming language
    """
    
    try:
        lambda_client.invoke(
            FunctionName='CodeSageAnalyzeLambda',
            InvocationType='Event',  # Async invocation
            Payload=json.dumps({
                'submission_id': submission_id,
                'language': language
            })
        )
        print(f"Triggered Analyze Lambda for {submission_id}")
        
    except Exception as e:
        print(f"Error triggering Analyze Lambda: {str(e)}")
