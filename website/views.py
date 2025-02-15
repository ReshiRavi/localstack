from flask import Blueprint,render_template,request
import boto3

views = Blueprint('views', __name__)
@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@views.route('/submit-form', methods=['GET', 'POST'])
def submit_form():
    userfile = request.files.get('userfile')
    print(request.headers)
    print(request.files)

    print(userfile.filename)
    if userfile:
        # You can save the file or process it as needed
        # Example: userfile.save(f"uploads/{userfile.filename}")
        s3 = boto3.client(
        service_name='s3',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        endpoint_url='http://localhost:4566/')
        print('S3 client done')
        print('s3: ', s3)
        response = s3.list_buckets()
        AWS_BUCKET_NAME = 'mybucket'
        print('s3 buckets list:', response['Buckets'])
        # Secure the filename before uploading
        filename = userfile.filename

        # Upload the file to S3
        try:
            s3.upload_fileobj(
                userfile,
                AWS_BUCKET_NAME,
                filename,
                ExtraArgs={"ContentType": userfile.content_type}
            )
            return 'File uploaded successfully to S3!'
        except Exception as e:
            return f'Error uploading file to S3: {str(e)}', 500

    else:
        return 'No file uploaded', 400