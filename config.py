import datetime

class Config:
    DB_HOST = 'mysqlinstance.cr2sp2mx5gjz.ap-northeast-2.rds.amazonaws.com'
    DB_USER = 'moschelin_db_user'
    DB_PASSWORD = 'moschelin123!@#'
    DB_DATABASE = 'moschelin_db'

    SALT = 'moschelin20230815'

    JWT_SECRET_KEY = 'moschelins_jwt'
    JWT_ACCESS_TOKKEN_EXPIRES = False
    PROPAGATE_EXCEPTIONS = True
    
    AWS_ACCESS_KEY_ID = 'AKIAR4D3TFNFFIUUJ56P'
    AWS_SECRET_ACCESS_KEY = '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'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
    
    S3_BUCKET = 'aws-moschelin-s3'
    S3_Base_URL = f'https://{S3_BUCKET}.s3.amazonaws.com/'
    
    GOOGLE_KEY = 'AIzaSyDPTSlAy52MeqFpGF3V7vcwR663Cxv02eM'

    
    
    
    