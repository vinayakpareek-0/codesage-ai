"""
Deploy Lambda functions to AWS.
Creates deployment packages and uploads them.
"""

import boto3
import zipfile
import os
import time

lambda_client = boto3.client('lambda', region_name='us-east-1')

# Role ARNs - get these from AWS Console → IAM → Roles
SUBMIT_ROLE_ARN = 'arn:aws:iam::991850590138:role/CodeSageSubmitLambdaRole'
ANALYZE_ROLE_ARN = 'arn:aws:iam::991850590138:role/CodeSageAnalyzeLambdaRole'
RESULT_ROLE_ARN = 'arn:aws:iam::991850590138:role/CodeSageResultLambdaRole'

def create_deployment_package(lambda_file, zip_name):
    """Create a zip file for Lambda deployment."""
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        zipf.write(f'lambda/{lambda_file}', lambda_file)
    print(f"✓ Created {zip_name}")

def deploy_lambda(function_name, zip_file, handler, role_arn, memory, timeout):
    """Deploy or update Lambda function."""
    
    with open(zip_file, 'rb') as f:
        zip_content = f.read()
    
    try:
        # Try to create new function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': zip_content},
            Timeout=timeout,
            MemorySize=memory,
            Description=f'CodeSage AI - {function_name}'
        )
        print(f"✓ Created Lambda: {function_name}")
        return response['FunctionArn']
        
    except lambda_client.exceptions.ResourceConflictException:
        # Function exists, update it
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        print(f"✓ Updated Lambda: {function_name}")
        return response['FunctionArn']

if __name__ == '__main__':
    print("=== Deploying Lambda Functions ===\n")
    
    # Create deployment packages
    print("Creating deployment packages...")
    create_deployment_package('submit_lambda.py', 'submit.zip')
    create_deployment_package('analyze_lambda.py', 'analyze.zip')
    create_deployment_package('result_lambda.py', 'result.zip')
    print()
    
    # Deploy Submit Lambda
    print("Deploying Submit Lambda...")
    submit_arn = deploy_lambda(
        function_name='CodeSageSubmitLambda',
        zip_file='submit.zip',
        handler='submit_lambda.handler',
        role_arn=SUBMIT_ROLE_ARN,
        memory=256,
        timeout=30
    )
    
    # Deploy Analyze Lambda
    print("Deploying Analyze Lambda...")
    analyze_arn = deploy_lambda(
        function_name='CodeSageAnalyzeLambda',
        zip_file='analyze.zip',
        handler='analyze_lambda.handler',
        role_arn=ANALYZE_ROLE_ARN,
        memory=512,
        timeout=300  # 5 minutes
    )
    
    # Deploy Result Lambda
    print("Deploying Result Lambda...")
    result_arn = deploy_lambda(
        function_name='CodeSageResultLambda',
        zip_file='result.zip',
        handler='result_lambda.handler',
        role_arn=RESULT_ROLE_ARN,
        memory=256,
        timeout=30
    )
    
    # Cleanup zip files
    os.remove('submit.zip')
    os.remove('analyze.zip')
    os.remove('result.zip')
    
    print("\n✓ All Lambda functions deployed!")
    print(f"\nSubmit Lambda ARN: {submit_arn}")
    print(f"Analyze Lambda ARN: {analyze_arn}")
    print(f"Result Lambda ARN: {result_arn}")
