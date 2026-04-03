"""
Script to create and configure S3 bucket for AI Code Reviewer.

This script:
1. Creates an S3 bucket with a unique name
2. Enables server-side encryption (SSE-S3)
3. Blocks public access
4. Adds lifecycle policy to delete old submissions
"""

import boto3
import json
from botocore.exceptions import ClientError

# Initialize S3 client
s3_client = boto3.client('s3')

# Bucket name - must be globally unique across ALL AWS accounts
# You'll need to change this to something unique
BUCKET_NAME = 'ai-code-reviewer-vinayak'

def create_bucket():
    """Create S3 bucket with encryption enabled."""
    try:
        print(f"Creating bucket: {BUCKET_NAME}")
        
        # Create bucket
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        print(f"✓ Bucket created: {BUCKET_NAME}")
        
        # Enable encryption
        s3_client.put_bucket_encryption(
            Bucket=BUCKET_NAME,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'  # S3-managed encryption
                        }
                    }
                ]
            }
        )
        print("✓ Encryption enabled (AES256)")
        
        # Block public access
        s3_client.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print("✓ Public access blocked")
        
        return True
        
    except ClientError as e:
        print(f"✗ Error creating bucket: {e}")
        return False

def configure_lifecycle():
    """Add lifecycle policy to delete submissions older than 30 days."""
    try:
        print("\nConfiguring lifecycle policy...")
        
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=BUCKET_NAME,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'ID': 'DeleteOldSubmissions',
                        'Status': 'Enabled',
                        'Filter': {
                            'Prefix': 'submissions/'
                        },
                        'Expiration': {
                            'Days': 30
                        }
                    }
                ]
            }
        )
        print("✓ Lifecycle policy configured (30-day deletion)")
        
        return True
        
    except ClientError as e:
        print(f"✗ Error configuring lifecycle: {e}")
        return False

if __name__ == '__main__':
    print("=== AI Code Reviewer S3 Setup ===\n")
    
    # Create bucket
    if create_bucket():
        # Configure lifecycle
        configure_lifecycle()
        print(f"\n✓ S3 setup complete!")
        print(f"Bucket name: {BUCKET_NAME}")
    else:
        print("\n✗ S3 setup failed")
