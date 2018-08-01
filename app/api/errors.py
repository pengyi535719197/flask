from flask import jsonify
from app.exceptions import ValidationError
from . import api




def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.stauts_code = 403
    return response

def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.stauts_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'Unauthorized', 'message': message})
    response.stauts_code = 401
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    # api中ValidationError异常处理
    return bad_request(e.args[0])