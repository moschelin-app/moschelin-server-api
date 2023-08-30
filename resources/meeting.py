from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql_connection import get_connection
from mysql.connector import Error

from config import Config
from utils import create_file_name, date_formatting

import boto3

# 모임 생성
class MeetingCreateResource(Resource):
    @jwt_required()
    def post(self):
        
        # body = ['form-data'] {
        #         'content' : '내용'
        #         'storeName' : '가게이름',
        #         'storeLat' : 위도,
        #         'storeLng' : 경도
        #         'date' : '날짜',
        #         'maximun' : 4,
        #         'image' : '이미지'
        #     }
        check_list = ['content', 'date', 'maximum', 'storeName', 'storeLat', 'storeLng', 'storeAddr']
        data = request.form
        
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목 데이터를 확인해주세요.'
                }, 400

        userId = get_jwt_identity()
        
        storeAddr = data.get('storeAddr')
        storeName = data.get('storeName')
        storeLat = data.get('storeLat')
        storeLng = data.get('storeLng')
        content = data.get('content')
        date = data.get('date')
        maximum = data.get('maximum')
        pay = data.get('pay')
        

        try:
            file_name = ''
            
            if 'photo' in request.files:
                file_name = create_file_name()
                
                s3 = boto3.client(
                    's3',
                    aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY
                )
                
                # 파일 업로드
                s3.upload_fileobj(
                    request.files['photo'],
                    Config.S3_BUCKET,
                    file_name,
                    ExtraArgs = {
                        'ACL' : 'public-read', # 모든 사람들이 사진을 볼수 있어야함. 권한 설정
                        'ContentType' : 'image/jpeg' # 올리는 모든 이미지의 타입을 jpg로 설정
                    }
                )
            
            
            connection = get_connection()
            
            # 가게 정보 찾아봄. 
            query = """
                select * 
                from store
                where name = %s and lat = %s and lng = %s;
            """
            record = (storeName, storeLat, storeLng)
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchone()

            # 등록된 가게가 없으면 추가함
            if result == None:
                query = '''
                    insert into store
                    (name, addr, lat, lng)
                    values
                    (%s,%s, %s, %s);
                '''
                record = (storeName,storeAddr, storeLat, storeLng)
                
                cursor = connection.cursor()
                cursor.execute(query, record)
                result = {
                    'id' : cursor.lastrowid
                }
                
            
            # 모임 등록
            query = '''
                insert into meeting
                (userId, storeId, content, date, maximum, photoURL, pay)
                values
                (%s, %s, %s ,%s, %s, %s, %s);
            '''
            record = (userId, result['id'], content, date, maximum, None if file_name == '' else Config.S3_Base_URL + file_name, 0 if pay == None else pay)
            
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
        except Exception as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        
        return {
            'result' : 'success'
        }


# 모임 URL
class MeetingResource(Resource):
    # 특정 모임 상세보기
    @jwt_required()
    def get(self, meetingId):
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            query = f'''
                select m.id, m.userId, m.storeId, m.content, m.date, m.photoURL as photo, m.maximum, m.pay, m.createdAt, m.updatedAt, 
                    u.nickname, u.profileURL as profile, s.name as storeName, s.addr as storeAddr,
                    s.lat as storeLat, s.lng as storeLng, count(ma.userId) as attend, if(m.userId = {userId}, 1, 0) isMine,
                    if(ma.userId = {userId}, 1, 0) isAttend
                from meeting m
                    join user u
                    on m.userId = u.id
                    join store s
                    on m.storeId = s.id
                    left join meeting_attend ma
                    on m.id = ma.meetingid
                where m.id = %s
                group by m.id;
            '''
            record = (meetingId, )
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchone()
            
            query = '''
                select u.profileURL as profile
                from meeting_attend ma
                    join user u
                    on ma.userId = u.id
                where ma.meetingId = %s;    
            '''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result['profiles'] = cursor.fetchall()
            
            # 날짜 포멧
            date_formatting(result)
            # 소수점 포멧
            # date_formatting(result)
            result['storeLat'] = float(result['storeLat'])
            result['storeLng'] = float(result['storeLng'])
            
            cursor.close()
            connection.close()
  
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500  
        
        return {
            'result' : 'success',
            'item' : result
        }
    
    # 특정 모임 수정
    @jwt_required()
    def put(self, meetingId):
        
        # body = ['form-data'] {
        #         'content' : '내용'
        #         'storeName' : '가게이름',
        #         'storeLat' : 위도,
        #         'storeLng' : 경도
        #         'date' : '날짜',
        #         'maximun' : 4,
        #         'image' : '이미지'
        #     }
        check_list = ['content', 'date', 'maximum', 'storeName', 'storeLat', 'storeLng', 'storeAddr']
        data = request.form
        
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목 데이터를 확인해주세요.'
                }, 400

        userId = get_jwt_identity()
        
        storeAddr = data.get('storeAddr')
        storeName = data.get('storeName')
        storeLat = data.get('storeLat')
        storeLng = data.get('storeLng')
        content = data.get('content')
        date = data.get('date')
        maximum = data.get('maximum')
        pay = data.get('pay')
        
        try:
            file_name = ''
            
            connection = get_connection()
            
            if 'photo' in request.files:
                file_name = create_file_name()
                
                s3 = boto3.client(
                    's3',
                    aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY
                )
                
                # 파일 업로드
                s3.upload_fileobj(
                    request.files['photo'],
                    Config.S3_BUCKET,
                    file_name,
                    ExtraArgs = {
                        'ACL' : 'public-read', # 모든 사람들이 사진을 볼수 있어야함. 권한 설정
                        'ContentType' : 'image/jpeg' # 올리는 모든 이미지의 타입을 jpg로 설정
                    }
                )
                
 
            # 등록된 모임이 있는지 확인
            query = '''
                select * 
                from meeting
                where userId = %s and id = %s;
            '''
            record = (userId, meetingId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            if len(result_list) == 0:
                return {
                    'result' : 'fail',
                    'error' : '수정할 모임이 존재하지 않습니다.'
                }, 402
            
            
            # 가게 정보 찾아봄. 
            query = """
                select * 
                from store
                where name = %s and lat = %s and lng = %s;
            """
            record = (storeName, storeLat, storeLng)
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchone()

            # 등록된 가게가 없으면 추가함
            if result == None:
                query = '''
                    insert into store
                    (name,addr, lat, lng)
                    values
                    (%s, %s, %s);
                '''
                record = (storeName,storeAddr ,storeLat, storeLng)
                
                cursor = connection.cursor()
                cursor.execute(query, record)
                result = {
                    'id' : cursor.lastrowid
                }
                
                
                
            # 모임 수정
            query = '''
                update meeting
                set storeId = %s, content = %s, date = %s, maximum = %s, photoURL = %s, pay = %s
                where userId = %s and id = %s;
            '''
            record = (result['id'], content, date, maximum, None if file_name == '' else Config.S3_Base_URL + file_name, 0 if pay == None else pay ,userId, meetingId)
            
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
        except Exception as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        
        return {
            'result' : 'success'
        }
    
    # 특정 모임 삭제
    @jwt_required()
    def delete(self, meetingId):
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            # 모임이 있는지 확인
            query = '''
                select *
                from meeting
                where userId = %s and id = %s;
            '''
            record = (userId, meetingId)
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            if len(result_list) == 0:
                return {
                    'result' : 'fail',
                    'error' : '삭제할 모임이 존재하지 않습니다.'
                }, 400
                
            query = '''
                delete from meeting
                where userId = %s and id = %s;
            '''
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' : 'success',
                'error' : str(e)
            }, 500
        
        
        return {
            'result' : 'success'
        }

# 모임 참가/취소
class MeetingAttendResource(Resource):
    # 모임 참가에 자신의 모임인지 확인해야함
    
    # 모임 참가
    @jwt_required()
    def post(self, meetingId):
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            # 이미 모임에 참가했는지 확인
            query = '''
                select *
                from meeting_attend
                where userId = %s and meetingId = %s;
            '''
            record = (userId, meetingId)
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            
            result_list = cursor.fetchall()
            if len(result_list) != 0:
                return {
                    'result' : 'fail',
                    'error' : '이미 모임에 참가했습니다.'
                }, 400
            
            # 모임 최대인원이 넘어갔는지 확인
            query = '''
                select maximum, count(ma.userId) as attend
                from meeting m
                    left join meeting_attend ma
                    on m.id = ma.meetingId
                where m.id = %s
                group by m.id;
            '''
            record_attend = (meetingId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record_attend)
            result = cursor.fetchone()
            if result['maximum'] == result['attend']:
                return {
                    'result' : 'fail',
                    'error' : '더 이상 모임에 참가할 수 없습니다.'
                }, 402
            
            
            
            query = '''
                insert into meeting_attend
                (userId, meetingId)
                values
                (%s, %s);
            ''' 
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
    
    # 모임 취소
    @jwt_required()
    def delete(self, meetingId):
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            # 모임에 참가한적이 있는지 확인
            query = '''
                select *
                from meeting_attend
                where userId = %s and meetingId = %s;
            '''
            record = (userId, meetingId)
            
            cursor = connection.cursor()
            cursor.execute(query,record)
            result_list = cursor.fetchall()
            if len(result_list) == 0:
                return {
                    'result' : 'fail',
                    'error' : '해당 모임에 참가하지 않았습니다.'
                }, 400
            
            
            # 모임 취소
            query = '''
                delete from meeting_attend
                where userId = %s and meetingId = %s;
            '''
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


# 위치 주위의 모임 리스트 가져오기
class MeetingGetAllResource(Resource):
    @jwt_required()
    def get(self):
        
        data = request.args
        
        # lat : 위도
        # lng : 경도
        # dis : 거리
        check_list = ['offset', 'limit', 'lat', 'lng', 'dis']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목을 확인하세요.'
                }, 400
                
        lat = data.get('lat')
        lng = data.get('lng')
        dis = data.get('dis')
        offset = data.get('offset')
        limit = data.get('limit')
                       
        try:
            connection = get_connection()
            
            # 설정한 거리안의 정보들을 불러옴
            query = f'''
                select m.id, m.userId, m.storeId, m.content, m.date, m.photoURL as photo, m.maximum,m.pay, m.createdAt, m.updatedAt
                , s.name as 'storeName', s.addr as 'storeAddr', s.lat as 'storeLat', s.lng as 'storeLng',s.distance, count(ma.userId) attend
                from (select id, name, addr, lat, lng, (6371*acos(cos(radians(lat))*cos(radians({lat}))*cos(radians({lng})

                    -radians(lng))+sin(radians(lat))*sin(radians({lat})))) as distance
                from store) s
                    join meeting m
                    on s.id = m.storeId
                    left join meeting_attend ma
                    on m.id = ma.meetingId
                where s.distance < {dis}
                group by m.id
                limit {offset}, {limit};
            '''
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result_list = cursor.fetchall()
            
            
            # 모임의 참가한 유저들의 프로필을 가져와서 모임 값에 넣음
            i = 0
            for result in result_list:
                query = f'''
                    select u.profileURL as profile
                    from meeting_attend ma
                        join user u 
                        on u.id = ma.userId and ma.meetingId = {result['id']};
                '''
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query)
                profiles = cursor.fetchall()
                result_list[i]['profiles'] = profiles
                # 날짜 포멧
                result_list[i]['date'] = result_list[i]['date'].isoformat()
                result_list[i]['createdAt'] = result_list[i]['createdAt'].isoformat()
                result_list[i]['updatedAt'] = result_list[i]['updatedAt'].isoformat()
                # 소수점 포멧
                result_list[i]['distance'] = float(result_list[i]['distance'])
                result_list[i]['storeLat'] = float(result_list[i]['storeLat'])
                result_list[i]['storeLng'] = float(result_list[i]['storeLng'])
                i += 1
            
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