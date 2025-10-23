import json, boto3, os, uuid
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

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

        bucket = os.environ.get('UPLOAD_BUCKET_NAME')
        if not bucket:
            return resp(500, {"error": "UPLOAD_BUCKET_NAME not set"})

        body = json.loads(event.get('body', '{}'))
        file_name = body.get('fileName')
        content_type = body.get('contentType') or "image/jpeg"  # default

        if not file_name:
            return resp(400, {"error": "fileName is required"})

        key = f"uploads/{uuid.uuid4()}-{file_name}"

        url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket, 'Key': key, 'ContentType': content_type},
            ExpiresIn=3600
        )

        return resp(200, {"uploadURL": url, "key": key, "contentType": content_type})

    except (ClientError, ValueError) as e:
        print("Presign error:", e)
        return resp(500, {"error": str(e)})
