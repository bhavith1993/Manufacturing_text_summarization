# Manufacturing Text Assistant (Amazon Bedrock + AWS SAM)

Serverless text assistant for manufacturing operators that generates practical SOP-style guidance using **Cohere Command R on Amazon Bedrock**. Deployed with **AWS SAM** using **API Gateway + Lambda**.

## Architecture
API Gateway (POST /assist) → Lambda → Amazon Bedrock (Cohere Command R)

## What it does
Accepts a structured JSON request (task, process, issue, constraints, audience, tone) and returns a concise, actionable response suitable for operators (e.g., SOP steps, safety checks, acceptance criteria).

## Infrastructure (Provisioned via AWS SAM)
The stack (defined in `template.yaml`) provisions:
- **API Gateway** (`/prod/assist`) to expose a POST endpoint
- **AWS Lambda** (`src/app.py`) to validate input, construct prompts, and call Bedrock
- **IAM policy (least privilege)** allowing only:
  - `bedrock:InvokeModel` on `cohere.command-r-v1:0`

Configured via environment variables:
- `BEDROCK_REGION=us-west-2`
- `MODEL_ID=cohere.command-r-v1:0`

## Deploy
Prereqs:
- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed

```bash
sam validate
sam build
sam deploy --guided
