from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql.connector import Error
from mysql_connection import get_connection

from utils import create_file_name, date_formatting, decimal_formatting
from config import Config

# 가계부 작성하기
class AccountBookResource(Resource):
    @jwt_required()
    def post(self):        
        
        userId = get_jwt_identity()
        
        data = request.get_json()
        check_list = ['storeName', 'date', 'price', 'payment']
        for check in check_list:
            if check not in data:
                return{
                    'result':'fail',
                    'error': '필수 항목이 존재하지 않습니다.'
                }, 400
        
        #     body - {
        #         'price' : 가격,
        #         'payment' : 카드, 
        #         'content' : 내용,
        #         'date' : 날짜
        #     }
        
        # storeId = data['storeId']
        storeName = data['storeName']
        
        date = data['date']
        accountBooksId = data['accountBooksId']
        price = data['price']
        payment = data['payment']
        content = data['content']
                
        try:
            connection = get_connection()
            
            # 가게정보 확인하기
            query = '''select id from store
                    where name = %s;
                    '''
            record = (storeName, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)                                
            result = cursor.fetchall()          

            
            # 등록된 가게가 없으면 추가함
            if result == None:
                query = '''
                    insert into store
                    (name)
                    values
                    (%s);
                '''
                record = (storeName, )             
                cursor = connection.cursor()
                cursor.execute(query, record)
                result = {
                    'id' : cursor.lastrowid
                }
            
            
            # 가계부 유저와 가게 정보 확인하기
            query = ''' 
                    select * 
                    from account_books
                    where id = %s 
                    and storeId = %s
                    and date = %s;
                    '''
            record = (userId, result[0]['id'], date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            result = cursor.fetchall()
        
            # 가계부에 정보가 없으면 가계부에 유저 정보와 가게정보를 담는다.
            if len(result) == None:
                query = '''
                        insert into account_books
                        (userId, storeId, date)
                        values
                        (%s, %s, %s);
                        '''
                record = (userId, result[0]['id'], date)
                cursor = connection.cursor()
                cursor.execute(query, record)
                result = {
                    'id' : cursor.lastrowid
                    }

            # 가계부 내용 입력하기.
            query = '''
                    insert into account_book
                    (accountBooksId, price, payment, storeName, content)
                    values
                    (%s, %s, %s, %s, %s);
                    '''                   
            record = (accountBooksId, price, payment, storeName, content)
            cursor = connection.cursor()
            cursor.execute(query, record)
            
            connection.commit()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result':'fail',
                'error' : str(e)
                }, 500
            
        # except Exception as e:
        #     return{
        #         'result':'fail',
        #         'error' : str(e)
        #     }, 500
        
        return {'result':'success'}