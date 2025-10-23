import json
import boto3
import os
import uuid
from botocore.exceptions import ClientError

# Initialize the S3
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Generates a pre-signed URL for uploading a file to an S3 bucket
    """
    try:
        # Get the bucket name from an environment variable
        bucket_name = os.environ.get('UPLOAD_BUCKET_NAME')
        if not bucket_name:
            raise ValueError("UPLOAD_BUCKET_NAME environment variable not set")

        body = json.loads(event.get('body', '{}'))
        file_name = body.get('fileName')
        
        if not file_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'fileName is required'}),
                'headers': {}
            }

        # Generate a unique key for the S3 object to prevent overwrites
        object_key = f"uploads/{uuid.uuid4()}-{file_name}"

        # Generate the pre-signed URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': object_key, 'ContentType': 'image/jpeg'},
            ExpiresIn=3600  # URL expires in 1 hour
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'uploadURL': presigned_url,
                'key': object_key
            }),
            'headers': {}
        }

    except (ClientError, ValueError) as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {}
        }