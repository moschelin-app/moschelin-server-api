from flask import request, jsonify
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql.connector import Error
from mysql_connection import get_connection

from decimal import Decimal
import json

# from utils import create_file_name, date_formatting, decimal_formatting
# from config import Config

# 가계부 내용 작성 관련
class AccountAddBookResource(Resource):
    
    # 가계부 작성하기
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
        price = data['price']
        payment = data['payment']
        content = data['content']
                
        try:
            connection = get_connection()
         
            # 가계부 유저와 가게 정보 확인하기
            query = ''' 
                    select * 
                    from account_books
                    where userId = %s 
                    and date = %s;
                    '''
            record = (userId, date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            result = cursor.fetchone()
        
           
            # 가계부에 정보가 없으면 가계부에 유저 정보를 담는다.
            if result == None:
                query = '''
                        insert into account_books
                        (userId, date)
                        values
                        (%s, %s);
                        '''
                record = (userId, date)
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
            record = (result['id'], price, payment, storeName, content)
            cursor = connection.cursor()
            cursor.execute(query, record)
            
            print(result)
            
            connection.commit()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result':'fail',
                'error' : str(e)
                }, 500
        
        return {'result':'success'}
    
    
class AccountBookResource(Resource):
    
    # 리뷰 수정하기.
    @jwt_required()
    def put(self, account_bookId):
        
        userId = get_jwt_identity()
        
        data = request.get_json()
        check_list = ['storeName', 'date', 'price', 'payment']
        for check in check_list:
            if check not in data:
                return{
                    'result':'fail',
                    'error': '필수 항목이 존재하지 않습니다.'
                }, 400
        
        storeName = data['storeName']
        
        # date = data['date']
        # accountBooksId = data['accountBooksId']
        price = data['price']
        payment = data['payment']
        content = data['content']
                
        try:
            connection = get_connection()
         
            # # 유저가 작성한 내용이 있는지 확인하기
            # query = ''' 
            #         select * 
            #         from account_books
            #         where date = %s and userId = %s 
            #         '''
            # record = (date, userId)
            # cursor = connection.cursor(dictionary=True)
            # cursor.execute(query,record)
            # result = cursor.fetchall()
    
            # if len(result) == 0:
            #     return {
            #         'result' : 'fail',
            #         'error' : '수정할 내용이 없습니다.'
            #     }, 402
            
            #  # 해당 날짜에 내용이 있다면 날짜를 수정해라
            # elif len(result) == 1:
            #     query = '''
            #             update account_books
            #             set date = %s
            #             where id = %s;
            #             '''
            #     record = (date, accountBooksId, userId)
            #     cursor = connection.cursor(prepared=True)
            #     cursor.execute(query,record)
            #     result.append({
            #         'id':cursor.lastrowid
            #         })
            # print(result)    
            # 가계부 내용이 있는지 확인하기
            # queryBooks = ''' 
            #         select id, payment, storeName as 'store', price
            #         from account_book
            #         where accountBooksId = %s;
            #         '''
            # recordBooks = (userId, )
            # cursor = connection.cursor(dictionary=True)
            # cursor.execute(queryBooks,recordBooks)
            # book_result = cursor.fetchall()
            
             # 가계부 내용 수정하기            
            query = '''
                    update account_book
                    set price = %s, payment = %s, storeName = %s, content = %s
                    where id = %s;
                    '''                   
            record = (price, payment, storeName, content, account_bookId)
            cursor = connection.cursor(prepared=True)
            cursor.execute(query, record)

            connection.commit()
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return{'result':'fail',
                   'error':str(e)
                   }, 500
        
        return {'result':'success'}
    
    # 가계부 삭제
    @jwt_required()
    def delete(self, account_bookId):
        
        # userId = get_jwt_identity()
        
        # data = request.get_json()
        # check_list = ['storeName', 'date', 'price', 'payment']
        # for check in check_list:
        #     if check not in data:
        #         return{
        #             'result':'fail',
        #             'error': '필수 항목이 존재하지 않습니다.'
        #         }, 400
        
        # #     body - {
        # #         'price' : 가격,
        # #         'payment' : 카드, 
        # #         'content' : 내용,
        # #         'date' : 날짜
        # #     }
        
        # # storeId = data['storeId']
        # storeName = data['storeName']
        
        # date = data['date']
        # accountBooksId = data['accountBooksId']
        
        try:
            connection = get_connection()
            
            
            # query = '''
            #         select * 
            #         from account_books
            #         where userId = %s 
            #         and id = %s;
            #     '''   
                                     
            # record = (userId, )
            # cursor = connection.cursor()
            # cursor.execute(query,record)
            # result = cursor.fetchall()
            
            # if len(result) == 0:
            #     return {
            #         'result' : 'fail',
            #         'error' : '삭제할 가계부 내용이 없습니다.'
            #     }, 400
            
            
            query = '''delete from account_book
                    where id  = %s;
                    '''   
                                     
            record = (account_bookId, )
            cursor = connection.cursor()
            cursor.execute(query,record)
            
            connection.commit()
            
            cursor.close()
            connection.close()        
            
        except Error as e:
            return{
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        return {
            'result' : 'success'
        }
    
    
# 가계부 월별 리스트   
class AccountBookMonthResource(Resource):
    
    @jwt_required()
    def get(self, month):
        
        userId = get_jwt_identity()
        
        
        
        try:
            connection = get_connection()
            
            query = f'''select abs.id, date_format(abs.date, '%m') as month, sum(ifnull(ab.price, 0)) as total
                    from account_books abs
                        left join account_book ab
                        on abs.Id = ab.accountBooksId
                    where abs.userId = %s
                    group by abs.userId;
                    '''
            record = (userId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            
            print(userId)
            print(result_list)
            
            cursor.close()
            connection.close()
            
        except Error as e:
            return{
                'result':'fail',
                'error':str(e)
            }, 500
            
        return jsonify({
                        'result':'success',
                        'count': len(result_list),
                        'items': result_list
                    })
    
    

# 가계부 당일 리스트 (상세보기)
class AccountBookDetailsResource(Resource):
    
    @jwt_required()
    def get(self, accountBooksId):
        
        userId = get_jwt_identity()    
        
        try:
            connection = get_connection()
            
            query = '''
                    select id, payment, storeName as 'store', price
                    from account_book
                    where accountBooksId = %s; 
                    '''
            record = (userId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            result = cursor.fetchall()
            
            # if len(result) == 0:
            #     return{
            #         'result' : 'fail',
            #         'error' : '작성된 가계부가 없습니다.'
            #     }, 400
            
            print(result)
            
        
            cursor.close()
            connection.close()
            
        except Error as e:
            return{
                'result':'fail',
                'error':str(e)
            }, 500

        return {
            'result':'success',
            'count': len(result),
            'items': result
            }
    