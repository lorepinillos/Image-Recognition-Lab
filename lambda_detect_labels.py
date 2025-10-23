import json
import boto3
from botocore.exceptions import ClientError

# Initialize Rekognition client
rekognition_client = boto3.client('rekognition')

def lambda_handler(event, context):
    """
    Calls Amazon Rekognition to detect labels in an image stored in S3.
    """
    try:
        body = json.loads(event.get('body', '{}'))
        bucket = body.get('bucket')
        key = body.get('key')

        if not bucket or not key:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'bucket and key are required'}),
                'headers': {}
            }
            
        # Call Rekognition's detect_labels API
        response = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10,
            MinConfidence=80
        )

        return {
            'statusCode': 200,
            'body': json.dumps(response['Labels']),
            'headers': {}
        }

    except ClientError as e:
        print(f"Rekognition Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Error processing image: {e.response['Error']['Code']}"}),
            'headers': {}
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {}
        }