from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql.connector import Error
from mysql_connection import get_connection

from utils import create_file_name, date_formatting, decimal_formatting
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
        storeName = data.get('storeName')
        storeLat = data.get('storeLat')
        storeLng = data.get('storeLng')
        content = data.get('content')
        rating = data.get('rating')
            
        try:
            connection = get_connection()
            
            # 가게정보 API
            # 가게정보 확인하기
            query = '''select id from store
                    where name = %s
                    and lat = %s
                    and lng = %s;'''
            record = (storeName, storeLat, storeLng)
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
                record = (storeName, storeLat, storeLng)
                cursor = connection.cursor()
                cursor.execute(query, record)
                result_list.append({
                    'id' : cursor.lastrowid
                    })

            # 리뷰 API    
            # 리뷰 글 작성 코드
            query = '''insert into review
                    (userId, storeId, content, rating)
                    values
                    (%s, %s, %s, %s);'''
            record = (userId, result_list[0]['id'], content, rating)
            cursor = connection.cursor()
            cursor.execute(query,record) 
            
            reviewId = cursor.lastrowid
            # 사진 API
            # 리뷰 사진 넣기
            if 'photo' in request.files:
                for photo in request.files.getlist('photo'):
                    # 이미지 파일 업로드를 위한 코드                
                    # print(current_time.isoformat().replace(':', '_').replace('.', '_') + '.jpg')
                    new_filename = create_file_name()
            
                    s3 = boto3.client(
                        's3',
                        aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY, 
                        # region_name = Config.AWS_S3_REGION_NAME
                    )
                    s3.upload_fileobj(
                        photo,
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
            
            
            if 'tag' in data:
                tags = data.getlist('tag')
                for tag in tags:
            # 태그 API
            # 태그 중복 확인
                    query = '''select * from tag
                            where name = %s;'''
                    record = (tag,)
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(query, record)
                    result_list = cursor.fetchall()

                    if len(result_list) == 0:
                        # 태그 넣기
                        query = '''insert into tag
                                    (name) values (%s);'''
                        record = (tag, )
                        cursor = connection.cursor()
                        cursor.execute(query,record)
                        result_list.append({
                            'id': cursor.lastrowid
                        })
                
                    # 리뷰태그 테이블의 정보 입력
                    query = '''insert into review_tag
                                (reviewId, tagId)
                                values
                                (%s, %s);'''
                    record = (reviewId, result_list[0]['id'])
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
        except Exception as e:
            return{'resutl':'fail',
                   'error':str(e)}, 500
                
        
        return{'result':'success'}
    
# 리뷰 수정 
class ReviewResource(Resource):
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
    
    @jwt_required()
    def get(self, reviewId):
        
        userId = get_jwt_identity()
    
      
        try:
            connection = get_connection()
            query = '''
                select r.*, s.id as storeId, s.name storeName,s.lat as storeLat, s.lng storeLng,
                count(rl.reviewId) as 'likes', count(rc.reviewId) as 'commentCnt', 
                count(rl_my.userId) as 'isLike'
                from review r
                    join store s
                    on r.storeId = s.id
                    left join review_likes rl
                    on rl.reviewId = r.id
                    left join review_comment rc
                    on rc.reviewId = r.id
                    left join review_likes rl_my
                    on rl_my.userId = %s
                where r.id = %s;
                '''
            record = (userId, reviewId)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            result_review = cursor.fetchone()
            # print(result)           
            
            query = '''
                select photoURL as photo
                from review_photo
                where reviewId = %s;
                '''
            record = (reviewId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            result_review['photos'] = cursor.fetchall()
            
            
            query = '''
                select t.name
                from review_tag rt
                    join tag t
                    on rt.tagId = t.id
                where reviewId = %s;
                '''
            record = (reviewId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_review['tags'] = cursor.fetchall()
            
            # connection.commit() # <- 생성, 수정, 삭제시에만 사용하는 코드 commit()을 사용한다.
                    
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return{
                'result':'fail',
                'error':str(e)
            }, 500
            
        # result_review['photos'] = result_photos
        # result_review['tags'] = result_tags
            
        # result_review = date_formatting(result_review)
        # result_review = decimal_formatting(result_review)
        
        # 날짜 포멧
        # result_review['createdAt'] = result_review['createdAt'].isoformat()
        # result_review['updatedAt'] = result_review['updatedAt'].isoformat()
        # 소수점 포멧
        # result_review['storeLat'] = float(result_review['storeLat'])
        # result_review['storeLng'] = float(result_review['storeLng'])


        return ({'result':'success',
                'item':decimal_formatting(date_formatting(result_review))
        })
    

# 리뷰 리스트 
class ReviewListResource(Resource):
    @jwt_required()
    def get(self):
        
        data = request.args
        
        check_list = ['lat', 'lng', 'offset', 'limit', 'dis']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목을 확인해야합니다.'
                }, 400
        
        lat = data.get('lat')
        lng = data.get('lng')
        dis = data.get('dis')
        offset = data.get('offset')
        limit = data.get('limit')
        
        
        userId = get_jwt_identity()
            
        try:
            connection = get_connection()
            
            query = f'''
                select r.*, u.nickname, ifnull(u.profileUrl, '') profile, s.name storeName, s.addr storeAddr, s.lat storeLat, s.lng storeLng
                    ,rp.photoURL photo, count(rc.id) commecntCnt, count(rl.reviewId) likeCnt, if(rl_my.userId, 1, 0) isLIke, s.dis
                from (select *, (6371*acos(cos(radians(lat))*cos(radians({lat}))*cos(radians({lng})

                    -radians(lng))+sin(radians(lat))*sin(radians({lat})))) as dis
                from store) s
                    join review r
                    on s.id = r.storeId
                    join user u 
                    on u.id = r.userId
                    left join review_photo rp
                    on r.id = rp.reviewId
                    left join review_comment rc
                    on rc.reviewId = r.id
                    left join review_likes rl
                    on rl.reviewId = r.id
                    left join review_likes rl_my
                    on rl_my.reviewId = r.id and rl_my.userId = %s
                where dis < %s
                group by r.id
                order by dis asc
                limit {offset}, {limit};
            '''
            record = (userId, dis)
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            
            
            for i in range(len(result_list)):
                query = '''
                    select t.name
                    from review_tag rt
                        join tag t
                        on t.id = rt.tagId and rt.reviewId = %s;
                '''
                
                record = (result_list[i]['id'], )
            
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list[i]['tags'] = cursor.fetchall()
                
                result_list[i] = decimal_formatting(date_formatting(result_list[i]))
                result_list[i]['rating'] = int(result_list[i]['rating'])
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' : 'fail',
                'error ': str(e)
            }, 500
            
         
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }