"""
Analyze Lambda Function

This Lambda analyzes code using AWS Bedrock's Claude 3 Sonnet model.
It retrieves code from S3, sends it to Bedrock, and stores the results.
"""

import json
import boto3
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Configuration
BUCKET_NAME = 'ai-code-reviewer-vinayak'
BEDROCK_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'

def handler(event, context):
    """
    Lambda handler - analyzes code using Bedrock AI.
    
    Args:
        event: Contains submission_id and language
        context: AWS Lambda runtime info
    
    Returns:
        None (stores result in S3)
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # Extract submission info
    submission_id = event['submission_id']
    language = event['language']
    
    print(f"Analyzing submission: {submission_id}, language: {language}")
    
    # Retrieve code from S3
    code = retrieve_code_from_s3(submission_id, language)
    if not code:
        print(f"Failed to retrieve code for {submission_id}")
        return
    
    # Build Bedrock prompt
    prompt = build_bedrock_prompt(code, language)
    
    # Call Bedrock
    analysis_text = invoke_bedrock(prompt)
    if not analysis_text:
        print(f"Failed to get Bedrock response for {submission_id}")
        return
    
    # Parse and validate response
    result = parse_bedrock_response(analysis_text, submission_id, language)
    if not result:
        print(f"Failed to parse Bedrock response for {submission_id}")
        return
    
    # Store result in S3
    store_result_in_s3(submission_id, result)
    
    print(f"Analysis complete for {submission_id}")


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


def retrieve_code_from_s3(submission_id, language):
    """
    Retrieve code from S3.
    
    Args:
        submission_id: Unique submission identifier
        language: Programming language
    
    Returns:
        Code string if successful, None if failed
    """
    
    try:
        extension = get_file_extension(language)
        s3_key = f'submissions/{submission_id}/code.{extension}'
        
        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=s3_key
        )
        
        code = response['Body'].read().decode('utf-8')
        print(f"Retrieved code from S3: {len(code)} bytes")
        return code
        
    except Exception as e:
        print(f"Error retrieving code from S3: {str(e)}")
        return None


def build_bedrock_prompt(code, language):
    """
    Build prompt for Bedrock code analysis.
    
    Args:
        code: Source code to analyze
        language: Programming language
    
    Returns:
        Formatted prompt string
    """
    
    prompt = f"""You are an expert code reviewer. Analyze the following {language} code and provide feedback in JSON format.

Code:
```{language}
{code}
```

Provide your analysis in this exact JSON structure:
{{
  "summary": "Brief overall assessment",
  "security_issues": [
    {{"severity": "critical|high|medium|low", "line": 1, "issue": "description", "recommendation": "fix"}}
  ],
  "performance_suggestions": [
    {{"line": 1, "issue": "description", "recommendation": "improvement"}}
  ],
  "code_quality_improvements": [
    {{"line": 1, "issue": "description", "recommendation": "improvement"}}
  ],
  "best_practices": [
    {{"issue": "description", "recommendation": "suggestion"}}
  ],
  "overall_score": 7
}}

Return ONLY the JSON, no other text."""
    
    return prompt


def invoke_bedrock(prompt, max_retries=1):
    """
    Call AWS Bedrock to analyze code.
    
    Args:
        prompt: The analysis prompt
        max_retries: Number of retries on failure
    
    Returns:
        Analysis text from Bedrock, or None if failed
    """
    
    for attempt in range(max_retries + 1):
        try:
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Call Bedrock
            response = bedrock_client.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            print(f"Bedrock response received: {len(analysis_text)} chars")
            return analysis_text
            
        except Exception as e:
            print(f"Bedrock error (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries:
                print("Retrying...")
            else:
                return None


def parse_bedrock_response(analysis_text, submission_id, language):
    """
    Parse Bedrock response into structured result.
    
    Args:
        analysis_text: Raw text from Bedrock
        submission_id: Submission identifier
        language: Programming language
    
    Returns:
        Structured result dict, or None if parsing failed
    """
    
    try:
        # Extract JSON from response (Claude sometimes adds text around it)
        start = analysis_text.find('{')
        end = analysis_text.rfind('}') + 1
        json_str = analysis_text[start:end]
        
        # Parse JSON
        analysis = json.loads(json_str)
        
        # Add metadata
        result = {
            'submission_id': submission_id,
            'language': language,
            'submitted_at': datetime.utcnow().isoformat(),
            'analyzed_at': datetime.utcnow().isoformat(),
            **analysis
        }
        
        print(f"Parsed result: score={result.get('overall_score')}")
        return result
        
    except Exception as e:
        print(f"Error parsing Bedrock response: {str(e)}")
        return None


def store_result_in_s3(submission_id, result):
    """
    Store analysis result in S3.
    
    Args:
        submission_id: Submission identifier
        result: Analysis result dict
    """
    
    try:
        s3_key = f'submissions/{submission_id}/result.json'
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(result, indent=2),
            ContentType='application/json'
        )
        
        print(f"Result stored in S3: {s3_key}")
        
    except Exception as e:
        print(f"Error storing result in S3: {str(e)}")
