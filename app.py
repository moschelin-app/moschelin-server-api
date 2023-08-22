from flask import Flask
from flask_restful import Api

from flask_jwt_extended import JWTManager
from config import Config

from resources.user import jwt_blocklist, UserRegisterResource, UserLoginResource, UserLogoutResource
from resources.meeting import MeetingCreateResource, MeetingGetAllResource, MeetingResource, MeetingAttendResource
from resources.search import SearchResentDeleteResource, SearchResource, SearchResentResource, SearchDetailResource, SearchRelationResource

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

api = Api(app)

api.add_resource(UserRegisterResource, '/user/register')
api.add_resource(UserLoginResource, '/user/login')
api.add_resource(UserLogoutResource, '/user/logout')

# 모임 생성
api.add_resource(MeetingCreateResource, '/meeting')
# 주위 위치에 따라 모임 가져오기
api.add_resource(MeetingGetAllResource, '/meeting/list')
# 모임 상세/수정/삭제
api.add_resource( MeetingResource , '/meeting/<int:meetingId>')
# 모임 참가/취소
api.add_resource( MeetingAttendResource , '/meeting/<int:meetingId>/attend')

# 검색 기능
api.add_resource(SearchResource, '/search')
# 검색 상세보기
api.add_resource(SearchDetailResource, '/search/detail')
# 최근 검색
api.add_resource(SearchResentResource, '/search/recent')
# 최근 검색 삭제
api.add_resource(SearchResentDeleteResource, '/search/recent/delete/<int:searchId>')
# 연관 검색
api.add_resource(SearchRelationResource, '/search/relation')



if __name__ == '__main__':
    app.run()