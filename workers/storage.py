import boto3
import os
from uuid import uuid4
from botocore.client import Config

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

PUBLIC_MINIO_URL = os.getenv("PUBLIC_MINIO_URL", "http://localhost:9000")

s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1"
)

def init_bucket():
    try:
        s3.head_bucket(Bucket=MINIO_BUCKET)
    except:
        s3.create_bucket(Bucket=MINIO_BUCKET)

        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{MINIO_BUCKET}/*"]
            }]
        }

        import json
        s3.put_bucket_policy(Bucket=MINIO_BUCKET, Policy=json.dumps(policy))


def upload_image(data: bytes, filename: str, content_type: str) -> str:
    key = f"images/{uuid4()}-{filename}"

    s3.put_object(
        Bucket=MINIO_BUCKET,
        Key=key,
        Body=data,
        ContentType=content_type
    )

    return f"{PUBLIC_MINIO_URL}/{MINIO_BUCKET}/{key}"
