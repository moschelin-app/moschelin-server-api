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
        }, 200
        
        
        
        