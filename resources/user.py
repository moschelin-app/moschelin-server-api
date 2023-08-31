from flask_restful import Resource
from flask import request

from email_validator import validate_email, EmailNotValidError
from utils import create_hash_passwrod, compare_hash_password
from mysql.connector import Error
from mysql_connection import get_connection

from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from utils import date_formatting, create_file_name, get_random_login_code
from config import Config

import boto3

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
        check_list = ['email', 'password', 'name', 'nickname']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목을 확인하세요.'
                }, 400

        try:
            validate_email(data['email'])
        except EmailNotValidError as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 401
            
        if len(data['password']) < 6:
            return {
                'result' : 'fail',
                'error' : '비밀번호는 최소 6자리 이상입니다.'
            }, 402
        
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
                    'error' : '이미 사용중인 이메일 입니다.'
                }, 403
                
                
            query = """
                select *
                from user
                where nickname = %s;
            """
            record = (data['nickname'], )
            cursor = connection.cursor()
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            if len(result_list) > 0:
                return {
                    'result' : 'fail',
                    'error' : '이미 사용중인 닉네임 입니다.'
                }, 405
            
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
                where email = %s and provider = 'email';
            '''
            record = (data['email'], )
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0:
                return {
                    'result' : 'fail',
                    'error' : '회원이 없습니다.'
                },  400

            if not compare_hash_password(data['password'], result_list[0]['password']):
                return {
                    'result' : 'fail',
                    'error' : '비밀번호가 다릅니다.'
                },  401
            
            cursor.close()
            connection.close()

        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500

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
    

# 유저 정보 수정
class UserInfoEditResource(Resource):
    # 유저 정보 수정
    @jwt_required()
    def put(self):
        
        userId = get_jwt_identity()
        
        data = request.form
        
        check_list = ['email', 'name', 'nickname']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목을 확인하세요.'
                }, 400
        
        email = data.get('email')
        name = data.get('name')
        nickname = data.get('nickname')
        
        # 이메일 유효성
        try:
            validate_email(email)
        except EmailNotValidError as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 402
        
        try:
            connection = get_connection()
            
            file_name = ''
            
            if 'profile' in request.files:
                file_name = create_file_name()
                
                s3 = boto3.client(
                    's3',
                    aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY
                )
                
                # 파일 업로드
                s3.upload_fileobj(
                    request.files['profile'],
                    Config.S3_BUCKET,
                    file_name,
                    ExtraArgs = {
                        'ACL' : 'public-read', # 모든 사람들이 사진을 볼수 있어야함. 권한 설정
                        'ContentType' : 'image/jpeg' # 올리는 모든 이미지의 타입을 jpg로 설정
                    }
                )
                
                # 수정
                query = '''
                    update user
                    set email = %s, nickname = %s, name = %s, profileURL = %s
                    where id = %s;
                '''
                record = (email, nickname, name, None if file_name == '' else Config.S3_Base_URL + file_name, userId)
                cursor = connection.cursor()
                cursor.execute(query, record)
                
            else :
                
                # 수정
                query = '''
                    update user
                    set email = %s, nickname = %s, name = %s
                    where id = %s;
                '''
                record = (email, nickname, name, userId)
                cursor = connection.cursor()
                cursor.execute(query, record)
            
            # 비밀번호 변경
            if 'password' in data:
                password = data.get('password')
                if len(password) < 6:
                    return {
                        'result' : 'fail',
                        'error' : '비밀번호는 최소 6자리 이상입니다.'
                    }, 403
                
                 # 비밀번호 암호화
                hash_password = create_hash_passwrod(password)
                    
                query = '''
                    update user
                    set password = %s
                    where id = %s;
                '''
                record = (hash_password, userId)
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

# 유저 정보
class UserInfoResource(Resource):
    # 유저 정보 확인
    @jwt_required()
    def get(self, user_id):
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            query = '''
                select id, email, nickname, name, profileURL profile, createdAt, updatedAt, if(id = %s, 1,0) isMine
                from user 
                where id = %s;
            '''
            record = (userId, user_id)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' : 'success',
                'error' : str(e)
            }, 500
        
        
        
        return {
            'result' : 'success',
            'item' : date_formatting(result)
        }

# 내 정보 확인
class UserMyInfoResource(Resource):
    @jwt_required()
    def get(self):
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            query = '''
                select id, email, nickname, name, profileURL profile, createdAt, updatedAt, if(id = %s, 1,0) isMine
                from user 
                where id = %s;
            '''
            record = (userId, userId)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        return {
            'result' : 'success',
            'item' : date_formatting(result)
        }        
        
# 유저 정보에서 유저가 작성한 리뷰 가져오기   
class UserInfoReviewResource(Resource):
    @jwt_required()
    def get(self, user_id):
        
        data = request.args
        
        check_lsit = ['offset', 'limit']
        for check in check_lsit:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목이 존재하지 않습니다.'
                }, 400
        
        offset = data.get('offset')
        limit = data.get('limit')
        
        try:
            connection = get_connection()
            
            query = f'''
                select r.id, ifnull(rp.photoURL, '') photo
                from user u
                    join review r
                    on r.userId = u.id and u.id = %s
                    left join review_photo rp
                    on r.id = rp.reviewId
                group by r.id
                order by r.createdAt desc
                limit {offset}, {limit};
            '''
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }
        
        
        
# 유저 정보에서 유저가 좋아요 누른 리뷰 가져오기
class UserInfoLikesResource(Resource):
    @jwt_required()
    def get(self, user_id):
        
        data = request.args
        
        check_lsit = ['offset', 'limit']
        for check in check_lsit:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목이 존재하지 않습니다.'
                }, 400
        
        offset = data.get('offset')
        limit = data.get('limit')
        
        try:
            connection = get_connection()
            
            query = f'''
                select r.id, ifnull(rp.photoURL, '') photo
                from user u
                    join review_likes rl
                    on u.id = rl.userId and u.id = %s
                    join review r
                    on r.id = rl.reviewId
                    left join review_photo rp
                    on r.id = rp.reviewId
                group by r.id
                order by rl.createdAt desc
                limit {offset}, {limit};
            '''
            record = (user_id, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        } 


# 카카오 로그인
class UserKakaoLoginResource(Resource):
    def post(self):
        
        data = request.get_json()
        
        check_list = ['kakaoId', 'email', 'name', 'profile']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목을 확인하세요.'
                }, 400
                
        try:
            connection = get_connection()
            
            query = '''
                select *
                from user
                where provider = 'kakao'
                    and providerId = %s
                    and email = %s;
            '''
            record = (data['kakaoId'], data['email'])
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchone()
            
            if result == None:
                
                name = f"{data['name']}_get_random_login_code()"
                
                query = '''
                    insert into user
                    (email, nickname, name, profileURL, provider, providerId)
                    values
                    (%s, %s, %s, %s,'kakao', %s);
                '''
                record = (data['email'], name, name, data['profile'], data['kakaoId'])
                cursor = connection.cursor()
                cursor.execute(query, record)
                
                result = {
                    'id' : cursor.lastrowid
                }         
                
                connection.commit()       
                
            
            cursor.close()
            connection.close()
            
            
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
            
        accessToken = create_access_token(result['id'])
        
        return {
            'result' : 'success',
            'accessToken' : accessToken
        }
        
        