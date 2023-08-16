from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql_connection import get_connection
from mysql.connector import Error

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
        check_list = ['content', 'date', 'maximum', 'storeName', 'storeLat', 'storeLng']
        data = request.form
        
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목 데이터를 확인해주세요.'
                }, 400

        user_id = get_jwt_identity()
                
        try:
            connection = get_connection()
            
            # 가게 정보 찾아봄. 
            query = """
                select * 
                from store
                where name = %s and lat = %s and lng = %s;
            """
            record = (data['storeName'], data['storeLat'], data['storeLng'])
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchone()

            # 등록된 가게가 없으면 추가함
            if result == None:
                query = '''
                    insert into store
                    (name, lat, lng)
                    values
                    (%s, %s, %s);
                '''
                record = (data['storeName'], data['storeLat'], data['storeLng'])
                
                cursor = connection.cursor()
                cursor.execute(query, record)
                result = {
                    'id' : cursor.lastrowid
                }
                
            
            # 모임 등록
            query = '''
                insert into meeting
                (userId, storeId, content, date, maximum)
                values
                (%s, %s, %s ,%s, %s);
            '''
            record = (user_id, result['id'], data['content'], data['date'], data['maximum'])
            
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


class MeetingGetAllResource(Resource):
    @jwt_required()
    def get(self):
        
        data = request.args
        
        check_list = ['offset', 'limit', 'lat', 'lng']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목을 확인하세요.'
                }, 400
                
        
        
        

        
        
        
        
        return {
            'result' : 'success',
            
        }