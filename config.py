import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smartkampung-secret-2026')

    DB_HOST     = os.environ.get('DB_HOST')
    DB_PORT     = os.environ.get('DB_PORT', '3306')
    DB_NAME     = os.environ.get('DB_NAME', 'smartkampung_db')
    DB_USER     = os.environ.get('DB_USER', 'admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION            = os.environ.get('AWS_REGION', 'ap-southeast-1')
    S3_BUCKET_NAME        = os.environ.get('S3_BUCKET_NAME', 'smartkampung-bucket')
    CLOUDFRONT_DOMAIN     = os.environ.get('CLOUDFRONT_DOMAIN', '')