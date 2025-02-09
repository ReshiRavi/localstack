#!/bin/sh
echo "Initializing localstack s3"

awslocal s3api create-bucket --bucket mybucket