import datetime
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    
    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_DATABASE = os.environ.get('DB_DATABASE')

    SALT = os.environ.get('SALT')

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKKEN_EXPIRES = False
    PROPAGATE_EXCEPTIONS = True
    
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=720)
    
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_Base_URL = f'https://{S3_BUCKET}.s3.amazonaws.com/'
    
    GOOGLE_KEY = os.environ.get('GOOGLE_KEY')
    
    NAVER_CLIENT_KEY = os.environ.get('NAVER_CLIENT_KEY')
    NAVER_SECRET_KEY = os.environ.get('NAVER_SECRET_KEY')
    

    
    
    
    