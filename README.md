# CodeSage AI

AI-powered code review system built with AWS serverless architecture. Submit code via REST API and get comprehensive analysis from Claude 3 Sonnet covering security, performance, code quality, and best practices.

## Architecture

```
API Gateway → Submit Lambda → S3 → Analyze Lambda → Bedrock (Claude) → S3 → Result Lambda
```

**Async Pattern**: Submit code, receive submission_id, poll for results when ready.

## Tech Stack

- **AWS Lambda** - 3 serverless functions (Submit, Analyze, Result)
- **AWS Bedrock** - Claude 3 Sonnet for AI analysis
- **AWS S3** - Storage for code submissions and results
- **AWS API Gateway** - REST API endpoints
- **Python 3.11** - Runtime and application logic

## Project Structure

```
ai-code-reviewer/
├── lambda/
│   ├── submit_lambda.py    # Handles code submissions
│   ├── analyze_lambda.py   # Calls Bedrock for analysis
│   └── result_lambda.py    # Retrieves analysis results
├── setup_s3.py             # S3 bucket setup script
├── deploy_lambdas.py       # Lambda deployment script
├── test_api.py             # End-to-end API test
└── requirements.txt        # Python dependencies
```

## Setup

1. **S3 Bucket**: Run `python setup_s3.py` to create bucket with encryption and lifecycle policy
2. **IAM Roles**: Create 3 roles in AWS Console (Submit, Analyze, Result) with appropriate S3/Bedrock/Lambda permissions
3. **Deploy Lambdas**: Run `python deploy_lambdas.py` to package and deploy all functions
4. **API Gateway**: Configure REST API with POST /submit and GET /result/{submission_id} endpoints
5. **Bedrock Access**: Enable Claude 3 Sonnet model in Bedrock console

## API Endpoints

**Submit Code**
```bash
POST /submit
Body: {"code": "...", "language": "python"}
Response: {"submission_id": "...", "status": "processing"}
```

**Get Results**
```bash
GET /result/{submission_id}
Response: {"summary": "...", "security_issues": [...], "overall_score": 8}
```

## Supported Languages

Python, JavaScript, TypeScript, Java, Go

## Learning Outcomes

This project demonstrates:
- AWS Lambda serverless architecture
- S3 object storage and lifecycle policies
- IAM roles and least-privilege security
- API Gateway REST API design
- AWS Bedrock GenAI integration
- Async processing patterns
- Error handling and CloudWatch logging

## Status

Experimental project for learning AWS ML/GenAI services. Core infrastructure deployed, debugging IAM permissions.
