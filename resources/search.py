from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql_connection import get_connection
from mysql.connector import Error

# 기본 검색 기능 (최대 3~5개만 보이도록 설정)
class SearchResource(Resource):
    @jwt_required()
    def get(self):
        
        userId = get_jwt_identity()
        
        search = request.args.get('search')
        
        if 'search' == None:
            return {
                'result' : 'fail',
                'error' : '검색어가 필요합니다.'
            }, 500


        try:
            connection = get_connection()
            
            # 사용자 검색어 저장을 시작
                # 검색어 저장되어 있는지 검색
            query = '''
                select id
                from user_search
                where search = %s;
            '''
            record = (search, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            search_result = cursor.fetchone()

                # 저장된 검색어가 없다면 검색어 저장
            if search_result == None:
                query = '''
                    insert into user_search
                    (search)
                    values
                    (%s);
                '''
                record = (search, )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                search_result = {
                    'id' : cursor.lastrowid
                }
            else :
                # 저장된 전체 검색어가 있다면 검색량 +1
                query = '''
                    UPDATE user_search 
                    SET searchCount = searchCount + 1 
                    WHERE id = %s;
                '''
                record = (search_result['id'], )
                cursor = connection.cursor()
                cursor.execute(query, record)
                
                
            # 전체 검색어 저장후 사용자 최근 검색어 저장
                # 만약 이미 최근 검색어에 있다면, 최신으로 변경해야한다.
            query = '''
                select *
                from my_search
                where searchId = %s and userId = %s;
            '''
            record = (search_result['id'], userId)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            search_result_list = cursor.fetchall()

            # 이전에 작성한 검색어가 없을경우 새로 추가해야하니 찾는다.
            if len(search_result_list) == 0:
                # 검색어의 갯수가 최대 10개까지 저장되도록 설정
                query = '''
                    select *
                    from my_search
                    where userId = %s
                    order by createdAt desc;
                '''
                record = (userId, )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                search_result_list = cursor.fetchall()
                
                # 검색된 갯수가 10개 이상이면
                if len(search_result_list) >= 10:
                    query = '''
                        delete from my_search
                        where id = %s;
                    '''
                    record = (search_result_list[-1]['id'], )
                    cursor = connection.cursor()
                    cursor.execute(query, record)
                    
            else: # 중복된 검색어가 있을경우에 삭제하자.
                # 최신으로 만들기 위해
                query = '''
                    delete from my_search
                    where searchId = %s;
                '''
                
                record = (search_result['id'], )
                cursor = connection.cursor()
                cursor.execute(query, record)
               
            
            # 최근 검색어 저장
            query = '''
                insert into my_search
                (searchId, userId)
                values
                (%s, %s);
            '''
            record = (search_result['id'], userId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            
            # 검색 유저
            
            
            # 검색 리뷰 
            
            
            # 검색 모임
            
            
            
            
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

# 최근 검색
class SearchResentResource(Resource):
    @jwt_required()
    def get(self):
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            query = '''
                select ms.id, us.search
                from my_search ms
                    join user_search us
                    on ms.searchId = us.id
                where ms.userId = %s;
            '''
            record = (userId,)
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            
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
        
# 최근 검색 삭제
class SearchResentDeleteResource(Resource):
    @jwt_required()
    def get(self, searchId):
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            query = '''
                delete from my_search
                where id = %s and userId = %s;
            '''
            record = (searchId, userId)
            
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
            'result' : 'success',
        }


# 검색 정보 상세보기
class SearchDetailResource(Resource):
    @jwt_required()
    def get(self):
        pass


    
# 연관 검색
class SearchRelationResource(Resource):
    @jwt_required()
    def get(self):
        search = request.args.get('search')
        
        try:
            connection = get_connection()
            
            query = f'''
                select *
                from user_search
                where search like '%{search}%'
                order by searchCount desc
                limit 10;
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
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }