from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql.connector import Error
from mysql_connection import get_connection


class ReviewLikeResource(Resource):
    
    # 좋아요 생성    
    @jwt_required()
    def post(self, reviewId):
        
        userId = get_jwt_identity()   
        
        try:
            connection = get_connection()
            
            query = '''
                    select *
                    from review
                    where id = %s;
                    '''
            record = (reviewId, )
            cursor = connection.cursor()
            cursor.execute(query, record)
            result = cursor.fetchall()
            if len(result) == 0:
                return {
                    'result' : 'fail',
                    'error' : '해당 리뷰를 찾을 수 없습니다.'
                }, 400
            
            query = '''
                    select *
                    from review_likes
                    where userId = %s and reviewId = %s;
                    '''
            record = (userId, reviewId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            result = cursor.fetchall()
            
            if len(result) >= 1:
                return {
                    'result' : 'fail',
                    'error' : '해당 리뷰에 이미 좋아요를 했습니다.'
                }, 402
            
            
            query = '''insert into review_likes 
                    (userId, reviewId)
                    values 
                    (%s, %s);'''
            record = (userId, reviewId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            
            connection.commit()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return{
                'result':'fail',
                'error':str(e)
            }, 500
            
        return{'result':'success'}
    
    # 좋아요 삭제        
    @jwt_required()
    def delete(self, reviewId):
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            query = '''
                    select *
                    from review
                    where id = %s;
                    '''
            record = (reviewId, )
            cursor = connection.cursor()
            cursor.execute(query, record)
            result = cursor.fetchall()
            if len(result) == 0:
                return {
                    'result' : 'fail',
                    'error' : '해당 리뷰를 찾을 수 없습니다.'
                }, 400
            
            
            query = '''delete from review_likes 
                    where userId = %s 
                    and reviewId = %s;'''
            record = (userId, reviewId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            
            connection.commit()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return{
                'result':'fail',
                'error':str(e)
            }, 500
        
        return{
            'result':'success'
        }
        
        
        
        