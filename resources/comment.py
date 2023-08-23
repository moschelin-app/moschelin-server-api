from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql.connector import Error
from mysql_connection import get_connection

# 리뷰 댓글 작성
class ReviewCommentResource(Resource):
    
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