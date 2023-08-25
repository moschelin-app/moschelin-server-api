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
                select s.*, avg(r.rating) as rating
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
        
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        
        try:
            connection = get_connection()
            
            
            query = f'''
                select r.*, u.id as uid , u.nickname, ifnull(u.profileURL, '') as profile , count(rl.reviewId) as likesCnt, if(rl_my.userId, 1, 0) as isLike
                from review r
                    join user u
                    on u.id = r.userId
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
                record = (result_list[i]['uid'], )
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
        
        userId = get_jwt_identity()
        
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        
        try:
            connection = get_connection()
            
            
            query = '''
                
            '''
            record = ()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' :'success',
                'error' : str(e)
            }, 500
        
        
        return {
            'result' : 'success'
        }