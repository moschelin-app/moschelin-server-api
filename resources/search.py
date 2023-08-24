from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql_connection import get_connection
from mysql.connector import Error

from utils import date_formatting, decimal_formatting

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


            # 검색 가게
                # 관련된 검색 중 평점이 가장 높은 1개를 보여줌
            query = f'''
                select s.id, s.name, s.addr, ifnull(avg(r.rating) ,0) as rating
                from store s
                    join review r
                    on s.id = r.storeId
                where s.name like '%{search}%' or s.addr like '%{search}%'
                group by s.id
                order by rating desc
                limit 1;
            '''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            store_search = cursor.fetchone()
            
            # 검색 유저
            query = f'''
                select u.id, u.email, u.nickname, u.name, u.profileURL as profile, u.createdAt, u.updatedAt, ifnull(avg(r.rating) ,0) as rating
                from user u
                    join review r
                    on u.id = r.userid
                where name like '%{search}%' or nickname like '%{search}%'
                group by u.id
                order by rating desc
                limit 1;
            '''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            user_search = cursor.fetchone()

                # 검색된 유저가 있다면, 리뷰 글도 검색
            if user_search != None:
                query = '''
                    select rp.photoURL as photo
                    from user u
                        join review r
                        on r.userId = u.id
                        join review_photo rp
                        on rp.reviewId = r.id
                    where u.id = %s
                    order by r.createdAt desc
                    limit 10;
                '''
                record = (user_search['id'], )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                user_search['reviews'] = cursor.fetchall()
                
                # 검색된 유저의 리뷰 게시물 갯수를 불러옴
                query = '''
                    select count(rp.reviewId) as reviewsCnt
                    from user u
                        join review r
                        on r.userId = u.id
                        join review_photo rp
                        on rp.reviewId = r.id
                    where u.id = %s;
                '''
                record = (user_search['id'], )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                               
                user_search['reviewsCnt'] = cursor.fetchone()['reviewsCnt']
                
            # 검색 리뷰 
            query = f'''
                select r.*, s.name, s.addr, count(rl.reviewid) as likeCnt, count(rl_my.userId) as isLike
                from review r
                    join store s
                    on r.storeId = s.id
                    left join review_likes rl
                    on rl.reviewId = r.id
                    left join review_likes rl_my
                    on rl_my.userId = %s
                where r.content like '%{search}%'
                order by r.rating desc
                limit 1;
            '''
            record = (userId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            review_search = cursor.fetchone()
            

            # 검색 모임
            query = f'''
                select m.*, u.profileURL as profile, count(ma.meetingId) as attend
                from meeting m
                    join user u
                    on m.userId = u.id
                    left join meeting_attend ma
                    on m.id = ma.meetingId
                where content like '%{search}%' and date > now()
                group by m.id
                order by date asc
                limit 1;
            '''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            meeting_search = cursor.fetchone()
            
            # 모임 게시판이 있다면 참여한 인원의 프로필을 가져오자
            if meeting_search != None:
                query = '''
                    select u.profileURL as profile
                    from meeting_attend ma
                        join user u
                        on ma.userId = u.id
                    where meetingId = %s;
                '''
                record = (meeting_search['id'], )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                meeting_search['profiles'] = cursor.fetchall()
  
            
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
            'item' : {
                'store' : decimal_formatting(date_formatting(store_search)),
                'user' : decimal_formatting(date_formatting(user_search)),
                'review' : date_formatting(review_search),
                'meeting' : date_formatting(meeting_search)
            }
        }
        
# 검색 상세보기
class SearchDetailStoreResource(Resource):
    @jwt_required()
    def get(self):
        
        data = request.args
        check_list = ['search', 'offset', 'limit']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목이 존재하지 않습니다.'
                }, 400

        search = data.get('search')
        offset = data.get('offset')
        limit = data.get('limit')
        
        userId = get_jwt_identity()
        
        
        try:
            connection = get_connection()
            
            query = f'''
                select s.id, s.name as storeName, s.addr,s.lat as storeLat, s.lng as storeLng, ifnull(avg(r.rating) ,0) as rating
                from store s
                    left join review r
                    on s.id = r.storeId
                where s.name like '%{search}%' or s.addr like '%{search}%'
                group by s.id
                order by rating desc
                limit {offset}, {limit};
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
            result_list[i] = decimal_formatting(date_formatting(result_list[i]))
        
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }


class SearchDetailUserResource(Resource):
    @jwt_required()
    def get(self):
        data = request.args
        check_list = ['search', 'offset', 'limit']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목이 존재하지 않습니다.'
                }, 400

        search = data.get('search')
        offset = data.get('offset')
        limit = data.get('limit')
        
        try:
            connection = get_connection()
            
            query = f'''
                select u.id, u.email, u.nickname, u.name, u.profileURL as profile, u.createdAt, u.updatedAt, ifnull(avg(r.rating) ,0) as rating
                from user u
                    left join review r
                    on u.id = r.userid
                where name like '%{search}%' or nickname like '%{search}%'
                group by u.id
                order by rating desc
                limit {offset}, {limit};
            '''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result_list = cursor.fetchall()
            
            for i in range(len(result_list)):
                # 검색된 유저가 있다면, 리뷰 글도 검색
                query = '''
                    select rp.photoURL as photo
                    from user u
                        join review r
                        on r.userId = u.id
                        join review_photo rp
                        on rp.reviewId = r.id
                    where u.id = %s
                    order by r.createdAt desc
                    limit 10;
                '''
                record = (result_list[i]['id'], )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list[i]['reviews'] = cursor.fetchall()
                
                # 검색된 유저의 리뷰 게시물 갯수를 불러옴
                query = '''
                    select count(rp.reviewId) as reviewsCnt
                    from user u
                        join review r
                        on r.userId = u.id
                        join review_photo rp
                        on rp.reviewId = r.id
                    where u.id = %s;
                '''
                record = (result_list[i]['id'], )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                            
                result_list[i]['reviewsCnt'] = cursor.fetchone()['reviewsCnt']
                
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
            
        for i in range(len(result_list)):
            result_list[i] = decimal_formatting(date_formatting(result_list[i]))
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }
    
class SearchDetailReviewResource(Resource):
    @jwt_required()
    def get(self):
        data = request.args
        check_list = ['search', 'offset', 'limit']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목이 존재하지 않습니다.'
                }, 400

        search = data.get('search')
        offset = data.get('offset')
        limit = data.get('limit')
        
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            
            query = f'''
                select r.*, s.name, s.addr, count(rl.reviewid) as likeCnt, count(rl_my.userId) as isLike
                from review r
                    join store s
                    on r.storeId = s.id
                    left join review_likes rl
                    on rl.reviewId = r.id
                    left join review_likes rl_my
                    on rl_my.userId = %s
                where r.content like '%{search}%'
                group by r.id
                order by r.rating desc
                limit {offset}, {limit};
            '''
            record = (userId, )
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
        
        for i in range(len(result_list)):
            result_list[i] = date_formatting(result_list[i])
            
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }
        
        
class SearchDetailMeetingResource(Resource):
    @jwt_required()
    def get(self):
        data = request.args
        check_list = ['search', 'offset', 'limit']
        for check in check_list:
            if check not in data:
                return {
                    'result' : 'fail',
                    'error' : '필수 항목이 존재하지 않습니다.'
                }, 400

        search = data.get('search')
        offset = data.get('offset')
        limit = data.get('limit')
        
        try:
            connection = get_connection()
            
            query = f'''
                select m.*, u.profileURL as profile, count(ma.meetingId) as attend
                from meeting m
                    join user u
                    on m.userId = u.id
                    left join meeting_attend ma
                    on m.id = ma.meetingId
                where content like '%{search}%' and date > now()
                group by m.id
                order by date asc
                limit {offset}, {limit};
            '''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result_list = cursor.fetchall()
            
            for i in range(len(result_list)):  
            # 모임 게시판이 있다면 참여한 인원의 프로필을 가져오자
                query = '''
                    select u.profileURL as profile
                    from meeting_attend ma
                        join user u
                        on ma.userId = u.id
                    where meetingId = %s;
                '''
                record = (result_list[i]['id'], )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list[i]['profiles'] = cursor.fetchall()
                
            cursor.close()
            connection.close()
            
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        for i in range(len(result_list)):
            result_list[i] = date_formatting(result_list[i])
            
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
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