from flask import jsonify, make_response


def Success(message="Successful"):
    return make_response(jsonify(message=message), 200)


def NotFound(message="Not found"):
    return make_response(jsonify(message=message), 404)


def BadRequest(message="Bad request"):
    return make_response(jsonify(message=message), 400)


def InternalError(message="Internal server error"):
    return make_response(jsonify(message=message), 500)
