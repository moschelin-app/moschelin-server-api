from flask_restful import Resource
from flask import request

from email_validator import validate_email, EmailNotValidError
from utils import create_hash_passwrod, compare_hash_password
from mysql.connector import Error
from mysql_connection import get_connection

from flask_jwt_extended import create_access_token, get_jwt, jwt_required


# 유저 회원가입
class UserRegisterResource(Resource):
    def post(self):
        
        # body - {
        #     email : "222@naver.com",
        #     nickname : "닉네임",
        #     name : "이름임",
        #     password : "1234"
        # }
        
        data = request.get_json()

        try:
            validate_email(data['email'])
        except EmailNotValidError as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 400
        
        # 비밀번호 암호화
        hash_password = create_hash_passwrod(data['password'])

        try:
            connection = get_connection()

            query = """
                select *
                from user
                where email = %s;
            """
            record = (data['email'], )
            cursor = connection.cursor()
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            if len(result_list) > 0:
                return {
                    'result' : 'fail',
                    'error' : '이미 있는 회원입니다.'
                }, 400
            
            query = '''
                insert into user
                (email, nickname, name, password)
                values
                (%s, %s, %s, %s);
            '''
            record = (data['email'], data['nickname'], data['name'], hash_password)

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500

        return {
            'result' : 'success'
        }
        

# 유저 로그인
class UserLoginResource(Resource):
    def post(self):

        # body - {
        #         "email" : "222@naver.com",
        #         "password" : "1234"
        #     }
        data = request.get_json()

        try :
            connection = get_connection()
            
            query = '''
                select * 
                from user
                where email = %s;
            '''
            record = (data['email'], )
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0:
                return {
                    'result' : 'fail',
                    'error' : '회원이 없습니다.'
                },  500

            if not compare_hash_password(data['password'], result_list[0]['password']):
                return {
                    'result' : 'fail',
                    'error' : '비밀번호가 다릅니다.'
                },  500
            
            cursor.close()
            connection.close()

        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }

        accessToken = create_access_token(result_list[0]['id'])

        return {
            'result' : 'success',
            'accessToken' : accessToken
        }
    

# 유저 로그아웃
jwt_blocklist = set()
class UserLogoutResource(Resource):
    @jwt_required()
    def delete(self):
        jti = get_jwt()['jti']
        jwt_blocklist.add(jti)

        return {
            'result' : 'success'
        }