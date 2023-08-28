from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql.connector import Error
from mysql_connection import get_connection

from utils import decimal_formatting, date_formatting

class MapsGetStoreResource(Resource):
    @jwt_required()
    def get(self):
        
        data = request.args
        
        check_list = ['lat', 'lng', 'dis']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목을 입력하세요.'
                }, 400
        
        lat = data.get('lat')
        lng = data.get('lng')
        dis = data.get('dis')
        
        try:
            connection = get_connection()
            
            query = f'''
            select s.id storeId, s.name storeName, s.lat storeLat, s.lng storeLng, ifnull(avg(r.rating), 0) rating
            from (select id, name,lat, lng, (6371*acos(cos(radians(lat))*cos(radians({lat}))*cos(radians({lng})

                -radians(lng))+sin(radians(lat))*sin(radians({lat})))) as distance
            from store) s
                left join review r
                on s.id = r.storeId
            where s.distance < {dis} and rating > 0
            group by s.id;
            '''
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result_list = cursor.fetchall()
            
            cursor.close()
            connection.close()
 
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
            
        for i in range(len(result_list)):
            result_list[i] = decimal_formatting(result_list[i])
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }
    
class MapGetReviewResource(Resource):
    @jwt_required()
    def get(self, storeId):
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            query = '''
                select r.*, s.name as storeName, s.addr as storeAddr, s.lat storeLat, s.lng storeLng, count(rl.reviewid) as likeCnt, if(rl_my.userId, 1, 0) as isLike
                from review r
                    join store s
                    on s.id = r.storeId
                    left join review_likes rl
                    on rl.reviewId = r.id
                    left join review_likes rl_my
                    on r.id = rl_my.reviewId and rl_my.userId = %s
                where s.id = %s
                group by r.id
                order by likeCnt desc
                limit 1;
            '''
            record = (userId, storeId)
            
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
            'item' : decimal_formatting(date_formatting(result))
        }