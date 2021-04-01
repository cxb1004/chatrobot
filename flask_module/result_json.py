from flask import jsonify

CODE_SUCCES = 0
CODE_FAIL = 999


def return_success(data):
    return_dict = {'code': CODE_SUCCES, 'info': '', 'data': data}
    return jsonify(return_dict)


def return_fail(errorMsg):
    return_dict = {'code': CODE_FAIL, 'info': errorMsg, 'data': ''}
    return jsonify(return_dict)


def return_fail_code(code, errorMsg):
    return_dict = {'code': code, 'info': errorMsg, 'data': ''}
    return jsonify(return_dict)


def jsonResultVo(code, message, data):
    return_dict = {'code': code, 'info': message, 'data': data}
    return jsonify(return_dict)
