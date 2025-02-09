#!/bin/bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages (if any)
pip3 install \
--platform manylinux2014_x86_64 \
--target=venv/lib/python3.13/site-packages \
--implementation cp \
--python-version 3.13 \
--only-binary=:all: --upgrade \
-r requirements.txt



# Package Lambda function
mkdir package
cp lambda_function.py package/
cp -r venv/lib/python3.*/site-packages/* package/

# Create deployment package
cd package
zip -r9 ../lambda_function.zip .
cd ..

awslocal s3api create-bucket --bucket mybucket

# Check if the Lambda function already exists
if awslocal lambda get-function --function-name my-lambda-function > /dev/null 2>&1; then
    echo "Updating existing Lambda function..."
    # Update Lambda function code
    # awslocal lambda update-function-code --function-name my-lambda-function \
    #     --zip-file fileb://lambda_function.zip
    awslocal lambda update-function-code --function-name my-lambda-function \
        --code S3Bucket=mybucket,S3Key=lambda_function.zip
else
    echo "Creating new Lambda function..."
    # Create Lambda function

    # awslocal lambda create-function --function-name my-lambda-function \
    #     --handler lambda_function.handler \
    #     --zip-file fileb://lambda_function.zip \
    #     --runtime python3.13 \
    #     --role arn:aws:iam::000000000000:role/execution_role
    awslocal lambda create-function \
        --function-name my-lambda-function \
        --runtime python3.13 \
        --role arn:aws:iam::000000000000:role/execution_role \
        --handler lambda_function.handler \
        --code S3Bucket=mybucket,S3Key=lambda_function.zip

fi

awslocal s3 cp lambda_function.zip s3://mybucket/lambda_function.zip

awslocal s3api put-bucket-notification-configuration \
--bucket mybucket \
--notification-configuration '{
    "LambdaFunctionConfigurations": [{
        "LambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:my-lambda-function",
        "Events": ["s3:ObjectCreated:*"]
    }]
}'

awslocal lambda add-permission --function-name my-lambda-function \
  --principal s3.amazonaws.com \
  --statement-id "12345" \
  --action "lambda:InvokeFunction" \
  --source-arn arn:aws:s3:::mybucket
# # Cleanup
# deactivate
# rm -rf venv package lambda_function.zip