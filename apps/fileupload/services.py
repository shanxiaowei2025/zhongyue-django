import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings

def generate_presigned_url(object_key, content_type=None, expiration=3600):
    """
    生成预签名上传URL，允许覆盖已存在的文件
    """
    try:
        s3_client = boto3.client('s3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            verify=False
        )
        
        params = {
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': object_key,
        }
        
        if content_type:
            params['ContentType'] = content_type
        
        url = s3_client.generate_presigned_url(
            'put_object',
            Params=params,
            ExpiresIn=expiration
        )
        
        return {
            'url': url,
            'path': object_key,
            'file_url': f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{object_key}",
            'expires_in': expiration
        }
        
    except ClientError as e:
        raise Exception(f"生成预签名URL失败: {str(e)}")