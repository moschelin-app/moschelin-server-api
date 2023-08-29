from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql.connector import Error
from mysql_connection import get_connection

from utils import date_formatting

# 리뷰 댓글 관련
class ReviewCommentResource(Resource):
    
    # 리뷰 댓글 전체
    @jwt_required()
    def get(self, reviewId):
        
        data = request.args
        
        check_list = ['offset', 'limit']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목을 입력해야합니다.'
                }, 400
        
        offset = data.get('offset')
        limit = data.get('limit')
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            query = f'''
                select rc.*, u.nickname, ifnull(u.profileURL, '') profile, if(u.id = {userId}, 1,0) isMine
                from review_comment rc
                    join review r
                    on rc.reviewId = r.id and r.id = {reviewId}
                    join user u
                    on rc.userId = u.id
                order by rc.createdAt desc
                limit {offset}, {limit};
            '''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result_list = cursor.fetchall()
            
            for i in range(len(result_list)):
                result_list[i] = date_formatting(result_list[i])
            
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
    
    # 리뷰 댓글 작성
    @jwt_required()
    def post(self, reviewId):
        
        userId = get_jwt_identity()
        
        data = request.get_json()
        

        try:
            connection = get_connection()
            query = '''insert into review_comment
                    (userId, reviewId, content)
                    values 
                    (%s, %s, %s);'''
            record = (userId, 1, data['content'])
            cursor = connection.cursor()
            cursor.execute(query, record)
            
            connection.commit()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return{
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        return{'result':'success'}
    

class ReviewCommentModResource(Resource):
    
    # 리뷰 댓글 수정 
    @jwt_required()
    def put(self, commentId):
        
        userId = get_jwt_identity()
        
        data = request.get_json()
  
        try:
            connection = get_connection()
            query = '''update review_comment
                    set content = %s
                    where id = %s and userId = %s;'''
            record = (data['content'], commentId, userId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            
            connection.commit()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return{
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        return{'result':'success'}
    
    
    #리뷰 댓글 삭제
    @jwt_required()
    def delete(self, commentId):
        
        userId = get_jwt_identity()
         
        try:
            connection = get_connection()
            query = '''delete drom review_comment
                    where id = %s
                    and userId = %s'''
            record = (commentId, userId)
            cursor = connection.cursor()
            cursor.execute(query,record)
            
            connection.commit()
            
            cursor.close()
            connection.close()

        except Error as e:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            return{
                'resutl':'fail',
                'error':str(e)
            }, 500
        
        return