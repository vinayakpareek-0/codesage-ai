"""
Result Lambda Function

This Lambda retrieves analysis results from S3 and returns them to the user.
It handles three states: completed, processing, and not found.
"""

import json
import boto3
from botocore.exceptions import ClientError

# Initialize AWS client
s3_client = boto3.client('s3')

# Configuration
BUCKET_NAME = 'ai-code-reviewer-vinayak'

def handler(event, context):
    """
    Lambda handler - retrieves analysis results.
    
    Args:
        event: Contains pathParameters with submission_id
        context: AWS Lambda runtime info
    
    Returns:
        API Gateway response with result or status
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # Extract submission_id from path
    submission_id = event['pathParameters']['submission_id']
    
    print(f"Retrieving result for: {submission_id}")
    
    # Check if result exists
    result = get_result_from_s3(submission_id)
    
    if result:
        # Result found - analysis complete
        return {
            'statusCode': 200,
            'body': json.dumps({
                'submission_id': submission_id,
                'status': 'completed',
                'result': result
            })
        }
    
    # Result not found - check if code exists (processing vs not found)
    if code_exists(submission_id):
        # Code exists but no result - still processing
        return {
            'statusCode': 202,
            'body': json.dumps({
                'submission_id': submission_id,
                'status': 'processing',
                'message': 'Analysis in progress. Please try again shortly.'
            })
        }
    
    # Neither code nor result exists - invalid submission_id
    return {
        'statusCode': 404,
        'body': json.dumps({
            'error': 'NotFound',
            'message': 'Submission ID does not exist',
            'submission_id': submission_id
        })
    }


def get_result_from_s3(submission_id):
    """
    Retrieve result from S3.
    
    Args:
        submission_id: Submission identifier
    
    Returns:
        Result dict if found, None otherwise
    """
    
    try:
        s3_key = f'submissions/{submission_id}/result.json'
        
        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=s3_key
        )
        
        result = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Result found: {s3_key}")
        return result
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"Result not found: {submission_id}")
            return None
        else:
            print(f"Error retrieving result: {str(e)}")
            return None


def code_exists(submission_id):
    """
    Check if code file exists in S3.
    
    Args:
        submission_id: Submission identifier
    
    Returns:
        True if code exists, False otherwise
    """
    
    try:
        # Try common extensions
        for ext in ['py', 'js', 'java', 'go', 'ts']:
            s3_key = f'submissions/{submission_id}/code.{ext}'
            
            s3_client.head_object(
                Bucket=BUCKET_NAME,
                Key=s3_key
            )
            
            print(f"Code found: {s3_key}")
            return True
            
    except ClientError:
        pass
    
    print(f"Code not found: {submission_id}")
    return False
