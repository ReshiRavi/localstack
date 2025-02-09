Hot reloading your Lambda functions locally with LocalStack allows you to see changes in your code immediately without needing to redeploy the entire function each time. Here is how you can set up hot reloading using Docker Compose, LocalStack, and a simple file watcher script.

### Step-by-Step Guide

1. **Create Docker Compose File:**
   Create a file named `docker-compose.yml` with the following content:

   ```yaml name=docker-compose.yml
   version: '3.8'

   services:
     localstack:
       image: localstack/localstack:latest
       ports:
         - "4566:4566"
         - "4571:4571"
       environment:
         - SERVICES=lambda
         - DEBUG=1
       volumes:
         - "./localstack:/docker-entrypoint-initaws.d"
         - "./lambda:/var/task"
   ```

2. **Create Lambda Function Code:**
   Create your Lambda function code in a directory named `lambda`. For example, create a file named `lambda_function.py` with the following content:

   ```python name=lambda/lambda_function.py
   def handler(event, context):
       return {
           'statusCode': 200,
           'body': 'Hello from Lambda!'
       }
   ```

3. **Create Deployment Script:**
   Create a script named `deploy_lambda.sh` in the `localstack` directory with the following content. This script will create a deployment package and upload the Lambda function to LocalStack:

   ```bash name=localstack/deploy_lambda.sh
   #!/bin/bash

   # Package Lambda function
   cd lambda
   zip -r ../lambda_function.zip .
   cd ..

   # Check if the Lambda function already exists
   if awslocal lambda get-function --function-name my-lambda-function > /dev/null 2>&1; then
       echo "Updating existing Lambda function..."
       # Update Lambda function code
       awslocal lambda update-function-code --function-name my-lambda-function \
           --zip-file fileb://lambda_function.zip
   else
       echo "Creating new Lambda function..."
       # Create Lambda function
       awslocal lambda create-function --function-name my-lambda-function \
           --runtime python3.8 \
           --handler lambda_function.handler \
           --role arn:aws:iam::000000000000:role/lambda-role \
           --zip-file fileb://lambda_function.zip
   fi

   # Cleanup
   rm -f lambda_function.zip
   ```

4. **Make the Script Executable:**
   Make the `deploy_lambda.sh` script executable by running the following command:

   ```bash
   chmod +x localstack/deploy_lambda.sh
   ```

5. **Create File Watcher Script:**
   Create a script named `file_watcher.sh` in the `localstack` directory to watch for changes in the Lambda function files and trigger the deployment script:

   ```bash name=localstack/file_watcher.sh
   #!/bin/bash

   while inotifywait -e modify,create,delete -r ./lambda; do
       ./deploy_lambda.sh
   done
   ```

6. **Make the File Watcher Script Executable:**
   Make the `file_watcher.sh` script executable by running the following command:

   ```bash
   chmod +x localstack/file_watcher.sh
   ```

7. **Run Docker Compose:**
   Start LocalStack using Docker Compose:

   ```bash
   docker-compose up
   ```

8. **Start the File Watcher:**
   In a new terminal, start the file watcher script to monitor changes and redeploy the Lambda function automatically:

   ```bash
   ./localstack/file_watcher.sh
   ```

### Summary

- The `docker-compose.yml` file sets up LocalStack with Lambda support.
- The `lambda/lambda_function.py` file contains your Lambda function code.
- The `localstack/deploy_lambda.sh` script handles the creation and updating of the Lambda function code in LocalStack.
- The `localstack/file_watcher.sh` script monitors changes in the Lambda function files and triggers the deployment script.
- Run `docker-compose up` to start LocalStack and `./localstack/file_watcher.sh` to enable hot reloading for your Lambda functions.

This setup ensures that any changes to your Lambda function code are automatically detected and deployed to LocalStack, enabling hot reloading for local development.


./localstack/deploy_lambda.sh