from flask import Flask
from flask_restful import Api

from flask_jwt_extended import JWTManager
from config import Config

from resources.user import jwt_blocklist, UserRegisterResource, UserLoginResource, UserLogoutResource, UserEmailFindResource
from resources.meeting import MeetingCreateResource, MeetingGetAllResource, MeetingResource, MeetingAttendResource
from resources.search import SearchResentDeleteResource, SearchResource, SearchResentResource, SearchRelationResource, SearchDetailMeetingResource, SearchDetailReviewResource, SearchDetailStoreResource, SearchDetailUserResource, SearchPlaceResource
from resources.review import ReviewAddResource, ReviewResource, ReviewListResource
from resources.comment import ReviewCommentModResource, ReviewCommentResource
from resources.like import ReviewLikeResource
from resources.maps import MapsGetStoreResource, MapGetReviewResource
from resources.store import StoreGetMeetingResource, StoreGetReviewResource, StoreResource

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
# 유저 이메일 찾기
api.add_resource(UserEmailFindResource, '/user/find/email')

# 리뷰 작성
api.add_resource( ReviewAddResource , '/review/add')
# 특정 리뷰 관련
api.add_resource( ReviewResource , '/review/<int:reviewId>')
# 리뷰 리스트 가져오기
api.add_resource(ReviewListResource, '/review/list')

# 리뷰 댓글 관련
api.add_resource( ReviewCommentResource , '/review/<int:reviewId>/comment')
# 특정 댓글 관련
api.add_resource( ReviewCommentModResource , '/review/comment/<commentId>')

# 리뷰 좋아요
api.add_resource( ReviewLikeResource , '/review/<int:reviewId>/like')

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
# 검색 상세보기 유저
api.add_resource(SearchDetailUserResource, '/search/user')
# 검색 상세보기 가게
api.add_resource(SearchDetailStoreResource, '/search/store')
# 검색 상세보기 리뷰
api.add_resource(SearchDetailReviewResource, '/search/review')
# 검색 상세보기 모임
api.add_resource(SearchDetailMeetingResource, '/search/meeting')
# 최근 검색
api.add_resource(SearchResentResource, '/search/recent')
# 최근 검색 삭제
api.add_resource(SearchResentDeleteResource, '/search/recent/delete/<int:searchId>')
# 연관 검색
api.add_resource(SearchRelationResource, '/search/relation')

# 모임, 리뷰에서 검색하는 가게 검색 (구글 API)
api.add_resource(SearchPlaceResource, '/search/place')


# 지도 상세보기에서 주위 가게 검색
api.add_resource(MapsGetStoreResource, '/maps')
# 지도 상세보기에서 가게 선택시 리뷰 보여줌
api.add_resource(MapGetReviewResource, '/maps/<int:storeId>')


# 가게 정보 상세보기
api.add_resource(StoreResource, '/store/<int:storeId>')
# 가게 상세보기에서 리뷰 정보 보여주기
api.add_resource(StoreGetReviewResource, '/store/<int:storeId>/review')
# 가게 상세보기에서 모임 정보 보여주기
api.add_resource(StoreGetMeetingResource, '/store/<int:storeId>/meeting')

if __name__ == '__main__':
    app.run()