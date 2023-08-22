from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql.connector import Error
from mysql_connection import get_connection

from datetime import datetime
from config import Config
import boto3


# 리뷰 작성
class ReviewAddResource(Resource):
    @jwt_required()
    def post(self):
        
        userId = get_jwt_identity()

        data = request.form
        

            # body  = [form-data]{
            #     'image' : 이미지,
            #     'content' : '내용',
            #     'storeName' : '가게이름',
            #     'storeAddress' : '가게주소',
            #     'tags' : [
            #         '#태그', '태그3'
            #     ],
            #     'ratings' : [
            #         '짠맛' : 5,
            #         '단맛' : 3
            #     ],

        try:
            connection = get_connection()
            
            # 가게정보 API
            # 가게정보 확인하기
            query = '''select id from store
                    where name = %s
                    and lat = %s
                    and lng = %s;'''
            record = (data['storeName'], data['storeLat'], data['storeLng'])
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)                                
            result_list = cursor.fetchall()
            # print('받아온 데이터 : ')
            # print(result_list)
            
            if len(result_list) == 0:
                # 가게 정보 작성하기
                query ='''insert into store
                        (name, lat, lng)
                        values
                        (%s, %s, %s);'''
                record = (data['storeName'], data['storeLat'], data['storeLng'])
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list.append({
                    'id' : cursor.lastrowid
                    })
            # print(result_list)                
            
            # 리뷰 API    
            # 리뷰 글 작성 코드
            query = '''insert into review
                    (userId, storeId, content)
                    values
                    (%s, %s, %s);'''
            record = (userId, result_list[0]['id'], data['content'])
            cursor = connection.cursor()
            cursor.execute(query,record) 
            
            reviewId = cursor.lastrowid
            
            # 사진 API
            # 리뷰 사진 넣기
            if 'photo' in request.files:
                # 이미지 파일 업로드를 위한 코드
                current_time = datetime.now()
                print(current_time.isoformat().replace(':', '_').replace('.', '_') + '.jpg')
                new_filename = current_time.isoformat().replace(':', '_').replace('.', '_') + '.jpg'
        
                s3 = boto3.client(
                    's3',
                    aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY, 
                    # region_name = Config.AWS_S3_REGION_NAME
                )
                s3.upload_fileobj(
                    request.files['photo'],
                    Config.S3_BUCKET,
                    new_filename,
                    ExtraArgs = {
                        'ACL' : 'public-read',
                        'ContentType' : 'image/jpeg'
                    }
                )
                
                query = '''insert into review_photo
                        (reviewId, photoURL)
                        values
                        (%s, %s);'''
                record = (reviewId, Config.S3_Base_URL+new_filename)
                cursor = connection.cursor()
                cursor.execute(query, record)
            
            # 태그 API
            # 태그 중복 확인
            query = '''select * from tag
                    where name = %s;'''
            record = [data['tag']]
            cursor = connection.cursor()
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            # print('태그의 이름은 : ')
            # print(result_list)
            
            if len(result_list) == 0:
                # 태그 넣기
                query = '''insert into tag
                            (name) values (%s);'''
                record = [data['tag']]
                cursor = connection.cursor()
                cursor.execute(query,record)
                result_list.append({
                    'id': cursor.lastrowid
                })
            
                # print(result_list)
                
                tagId = cursor.lastrowid
                
                # 리뷰태그 테이블의 정보 입력
                query = '''insert into review_tag
                            (reviewId, tagId)
                            values
                            (%s, %s);'''
                record = (reviewId, tagId)
                cursor = connection.cursor()
                cursor.execute(query,record) 
            
            print(dict(data['rating'])['짠맛'])
            # 별점 API
            # 별점 중복 체크하기.
            query = '''select * from rating
                        where name = %s;'''
            record = [data['rating']]
            cursor = connection.cursor()
            cursor.execute(query,record) 
            result_list = cursor.fetchall()
            print('별점 : ')
            print(result_list)
            
            if len(result_list) == 0:
                # 별점 넣기
                query = '''insert into rating
                            (name) values (%s);'''
                record = [data['rating']]
                cursor = connection.cursor()
                cursor.execute(query,record)
                result_list.append({
                    'id': cursor.lastrowid
                })
            
                print(result_list)
                
            ratingId = cursor.lastrowid
                
            # 별점 테이블의 정보 입력
            query = '''insert into review_rating
                    (reviewId, ratingId, rating)
                    values
                    (%s, %s, %s);'''
            record = (reviewId, ratingId, data['rating'])
            cursor = connection.cursor()
            cursor.execute(query,record) 
            return
            
            connection.commit()
            
            cursor.close()
            connection.close()        
            
            cursor.lastrowid
            
        except Error as e:
            return{
                'result' : 'fail',
                'error' : str(e)
            }, 500
        except Exception as e:
            return{'resutl':'fail',
                   'error':str(e)}, 500
                
        
        return{'result':'success'}
    
# 리뷰 수정 
class ReviewModifyResource(Resource):
    @jwt_required()
    def put(self, reviewId):
        
        userId = get_jwt_identity()

        data = request.form

            # body  = [form-data]{
            #     'image' : 이미지,
            #     'content' : '내용',
            #     'storeName' : '가게이름',
            #     'storeAddress' : '가게주소',
            #     'tags' : [
            #         '#태그', '태그3'
            #     ],
            #     'ratings' : [
            #         '짠맛' : 5,
            #         '단맛' : 3
            #     ],

        try:
            connection = get_connection()
            query = '''update review
                    set content = %s
                    where id = %s;'''   
                                     
            record = (data['content'], reviewId)
            cursor = connection.cursor()
            cursor.execute(query,record)
            
            connection.commit()
            
            cursor.close()
            connection.close()        
            
        except Error as e:
            return{
                'result' : 'fail',
                'error' : str(e)
            }, 500
                
        
        return{'result':'success'}

# 리뷰 삭제
class ReviewDeleteResource(Resource):
    @jwt_required()
    def delete(self, storeId):
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            query = '''delete from review
                    where id  = %s
                    and userId = %s;'''   
                                     
            record = (storeId, userId)
            cursor = connection.cursor()
            cursor.execute(query,record)
            
            connection.commit()
            
            cursor.close()
            connection.close()        
            
        except Error as e:
            return{
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        return
 
# 리뷰 상세보기
class ReviewDetailsResource(Resource):
    
    @jwt_required()
    def get(self, reviewId):
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            query = '''
                    dd
                    '''
            record = ()
            cursor = connection.cursor()
            cursor.execute(query,record)
            
            connection.commit()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return{
                'result':'fail',
                'error':str(e)
            }, 500
        
        return

# 리뷰 리스트 
class ReviewListResource(Resource):
    def get(self):
        
        try:
            self
            
        except Error as e:
            return
        
        return