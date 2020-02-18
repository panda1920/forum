import os
import boto3
from pathlib import Path
import logging

IMAGE_PATH = Path(r'C:\Users\pontdemon\Desktop\tutorial-images')
IMAGE_FILENAME = IMAGE_PATH / 'mountain.jpeg'
BUCKET_NAME = 'kamigama-myforumapp'
REGION_NAME = os.getenv('AWS_DEFAULT_REGION')

s3 = boto3.resource('s3')
client = boto3.client('s3')

# s3.create_bucket(
#     Bucket=BUCKET_NAME,
#     CreateBucketConfiguration={
#         'LocationConstraint': 'ap-northeast-1'
#     }
# )

def list_buckets():
    for bucket in s3.buckets.all():
        print(bucket)

def list_objects(bucket_name):
    objects = client.list_objects_v2(Bucket=bucket_name)['Contents']
    return objects

def add_url_to_objects(objects, bucket_name, region_name):
    for obj in objects:
        key = obj['Key']
        obj['url'] = f'https://{bucket_name}.s3-{region_name}.amazonaws.com/{key}'

    return objects

def upload_file(file_name, bucket_name, object_name):
    logging.info('Uploading file {file_name} to bucket {bucket_name}')
    client.upload_file(
        file_name,
        bucket_name,
        object_name,
        ExtraArgs=dict(ACL='public-read')
    )

def upload_binary(file_name, bucket_name, object_name):
    with open(file_name, 'rb') as fp:
        binary = fp.read()
        client.put_object(
            ACL='public-read',
            Body=binary,
            Bucket=bucket_name,
            Key=object_name
        )

def download_file(file_name, bucket_name, object_name):
    client.download_file(
        bucket_name,
        object_name,
        file_name
    )

NEW_FILE_PATH = IMAGE_PATH / 'mountain2.jpeg'

try:
    # upload_binary(str(IMAGE_FILENAME), BUCKET_NAME, 'images/moutain.jpeg')
    # download_file(str(NEW_FILE_PATH), BUCKET_NAME, 'images/moutain.jpeg')
    objects = list_objects(BUCKET_NAME)
    objects = add_url_to_objects(objects, BUCKET_NAME, REGION_NAME)
    print(objects)

except Exception as e:
    logging.error(e)