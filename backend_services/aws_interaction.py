from typing import Optional

import boto3
from fastapi import UploadFile

import os
from dotenv import load_dotenv

load_dotenv()

bucket_name = os.getenv('S3_BUCKET_NAME')
# profile_name = os.getenv('AWS_PROFILE_NAME')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
region = os.getenv('AWS_REGION')

def generate_aws_file_link(bucket_name: str, region: str, aws_name: str):
    return f'https://{bucket_name}.s3.{region}.amazonaws.com/{aws_name}'


def upload_file_to_s3_from_api(file: UploadFile, aws_file_name: Optional[str] = None):
    session = boto3.Session(
        # profile_name=profile_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region
    )
    client = session.client('s3')
    file.file.seek(0) #search for the beginning of the file
    aws_name = aws_file_name if aws_file_name is not None else file.filename
    client.upload_fileobj(file.file, bucket_name, aws_name)

    return generate_aws_file_link(bucket_name=bucket_name, region=region, aws_name=aws_name)