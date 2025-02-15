import json
from pymongo import MongoClient
import certifi
import boto3
import fitz
from botocore.exceptions import NoCredentialsError, ClientError

mongo_connet = 'mongodb+srv://test:test@reshiflaskintro.8jhk4.mongodb.net?retryWrites=true&w=majority'
client = MongoClient(mongo_connet,tlsCAFile=certifi.where())

# Access the database
db = client.user_db
records = db['user_records']

def lambda_handler(event, context):
    print('test')
    file_name = event['Records'][0]['s3']['object']['key']
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    print('file_name:', file_name)
    print('bucket_name', bucket_name)

    s3 = boto3.client(
            service_name='s3',
            aws_access_key_id='test',
            aws_secret_access_key='test',
            endpoint_url='http://localstack:4566',
    )
    print('S3 client done')
    print('s3: ', s3)
    response = s3.list_buckets()
    print('response:', response['Buckets'])
    file_path = '/tmp/'+ file_name
    try:
        # Set the ACL to 'public-read' for the object
        s3.put_object_acl(Bucket=bucket_name, Key=file_name, ACL='public-read')
        print(f"ACL set to 'public-read' for object: {file_name}")
    except ClientError as e:
        print(f"Error setting ACL: {e}")
    try:
        s3.head_object(Bucket=bucket_name, Key=file_name)
        print("File exists.")
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print("File not found.")
        else:
            print("An error occurred:", e)

    try:
        # Download the file
        s3.download_file(bucket_name, file_name, file_path)
        print(f"File downloaded successfully to {file_path}")
    except NoCredentialsError:
        print("Credentials not available")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"The bucket '{bucket_name}' does not exist")
        elif error_code == 'NoSuchKey':
            print(f"The file '{file_name}' does not exist in bucket '{bucket_name}'")
        else:
            print(f"An error occurred: {e}")
    print('Download complete')
    pdf_file = fitz.open(file_path)
    text = ''

    for page_num in range(pdf_file.page_count):
        page = pdf_file.load_page(page_num)
        text += page.get_text()

    document = {
        "pdf_name": file_name,
        "text" : text
    }
    print('text:', text)

    result = records.insert_one(document)

    print('result for inserting record', result)

    print('message received:', json.dumps(event, indent=2))
    return {
        'statusCode': 200,
        'body': json.dumps('File uploaded and lambda triggered and inserted in mongoDB')

    }

# x = {
#     'Records':[{
#         's3':{
#             'object': {
#                 'key': 'YESBANK4.pdf'
#             },
#             'bucket': {
#                 'name': 'mybucket'
#             }
#         }
#     }
#     ]
# }
# lambda_handler(x, {})