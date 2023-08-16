from flask import request
from flask_restful import Resource

from flask_jwt_extended import jwt_required, get_jwt_identity

class MeetingCreateResource(Resource):
    @jwt_required()
    def post(self):
        data = request.form
        print(data)
        
        return
