import json, boto3
from botocore.exceptions import ClientError

rekognition = boto3.client('rekognition')

CORS = {
    "Access-Control-Allow-Origin": "https://lorepinillos.github.io",
    "Access-Control-Allow-Headers": "Content-Type,x-api-key",
    "Access-Control-Allow-Methods": "OPTIONS,POST"
}

def resp(code, body):
    return {"statusCode": code, "headers": CORS, "body": json.dumps(body)}

def lambda_handler(event, context):
    try:
        if event.get("httpMethod") == "OPTIONS":
            return resp(200, {})  # preflight

        body = json.loads(event.get('body', '{}'))
        bucket, key = body.get('bucket'), body.get('key')
        if not bucket or not key:
            return resp(400, {"error": "bucket and key are required"})

        out = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10, MinConfidence=80
        )
        return resp(200, out['Labels'])

    except ClientError as e:
        print("Rekognition error:", e)
        return resp(500, {"error": e.response['Error']['Code']})
    except Exception as e:
        print("Error:", e)
        return resp(500, {"error": str(e)})
