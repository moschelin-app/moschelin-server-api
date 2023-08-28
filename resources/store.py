from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql_connection import get_connection
from mysql.connector import Error

from utils import date_formatting, decimal_formatting

# 가게 정보 불러오기
class StoreResource(Resource):
    @jwt_required()
    def get(self, storeId):
        try:
            connection = get_connection()
            
            # 평균 별점과 같이 들고온다.
            query = '''
                select s.id storeId, s.name storeName,s.addr storeAddr, s.lat storeLat, s.lng storeLng, avg(r.rating) as rating
                from store s
                    join review r
                    on s.id = r.storeId
                where s.id = %s;
            '''
            record = (storeId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' :'success',
                'error' : str(e)
            }, 500
            
            
        
        return {
            'result' : 'success',
            'item' : decimal_formatting(date_formatting(result))
        }

# 가게 정보에서 리뷰 리스트 가져오기
class StoreGetReviewResource(Resource):
    @jwt_required()
    def get(self, storeId):
        userId = get_jwt_identity()
        
        data = request.args
        
        check_list = ['offset', 'limit']
        for check in check_list:
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
                select r.*, ifnull(rp.photoURL, '') photo, u.nickname, ifnull(u.profileURL, '') as profile 
		            , count(rl.reviewId) as likesCnt, if(rl_my.userId, 1, 0) as isLike, if(r.userId = {userId}, 1, 0) isMine
                from review r
                    join user u
                    on u.id = r.userId
                    left join review_photo rp
                    on r.id = rp.reviewId
                    left join review_likes rl
                    on r.id = rl.reviewId
                    left join review_likes rl_my
                    on r.id = rl_my.reviewId and rl_my.userId = %s
                where r.storeId = %s
                group by r.id
                order by createdAt desc
                limit {offset}, {limit};
            '''
            record = (userId, storeId)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            
            for i in range(len(result_list)):
                # 유저 리뷰 갯수 
                query = '''
                    select count(*) reviewCnt
                    from user u
                        join review r
                        on u.id = r.userId
                    where u.id = %s;
                '''
                record = (result_list[i]['userId'], )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list[i]['reviewCnt'] = cursor.fetchone()['reviewCnt']
                
                # 해당 리뷰 게시물 태그
                query = '''
                    select t.name
                    from review_tag rt
                        join tag t
                        on rt.tagId = t.id
                    where reviewId = %s;
                '''
                record = (result_list[i]['id'], )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list[i]['tags'] = cursor.fetchall()
                
                result_list[i] = date_formatting(result_list[i])
            
            
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' :'success',
                'error' : str(e)
            }, 500
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }

class StoreGetMeetingResource(Resource):
    @jwt_required()
    def get(self, storeId):
        
        data = request.args
        
        check_list = ['offset', 'limit']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목이 존재하지 않습니다.'
                }, 400
        
        offset = data.get('offset')
        limit = data.get('limit')
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            
            query = f'''
                select m.id, m.userId, m.storeId, m.content, m.date, ifnull(m.photoURL, '') photo, m.maximum, m.createdAt, m.updatedAt
                    , u.nickname, ifnull(u.profileURL, '') as profile, count(ma.meetingId) attend, if(m.userId = {userId}, 1, 0) isMine
                from store s
                    join meeting m
                    on s.id = m.storeId
                    join user u
                    on u.id = m.userId
                    left join meeting_attend ma
                    on m.id = ma.meetingId
                where s.id = %s and date > now()
                group by m.id
                order by date asc
                limit {offset}, {limit};
            '''
            record = (storeId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            
            for i in range(len(result_list)):
                query = f'''
                    select ifnull(u.profileURL , '') profile
                    from meeting_attend ma
                        join meeting m
                        on ma.meetingId = m.id
                        join user u
                        on ma.userId = u.id
                    where m.id = %s;
                '''
                record = (result_list[i]['id'], )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list[i]['profiles'] = cursor.fetchall()
                
                result_list[i] = date_formatting(result_list[i])
            
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' :'success',
                'error' : str(e)
            }, 500
        
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }