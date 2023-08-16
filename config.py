class Config:
    DB_HOST = 'mysqlinstance.cr2sp2mx5gjz.ap-northeast-2.rds.amazonaws.com'
    DB_USER = 'moschelin_db_user'
    DB_PASSWORD = 'moschelin123!@#'
    DB_DATABASE = 'moschelin_db'

    SALT = 'moschelin20230815'

    JWT_SECRET_KEY = 'moschelins_jwt'
    JWT_ACCESS_TOKKEN_EXPIRES = False
    PROPAGATE_EXCEPTIONS = True