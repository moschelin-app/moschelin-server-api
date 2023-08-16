from flask import Flask
from flask_restful import Api

from flask_jwt_extended import JWTManager
from config import Config

from resources.user import jwt_blocklist, UserRegisterResource, UserLoginResource, UserLogoutResource
from resources.meeting import MeetingCreateResource, MeetingGetAllResource, MeetingResource, MeetingAttendResource

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



if __name__ == '__main__':
    app.run()