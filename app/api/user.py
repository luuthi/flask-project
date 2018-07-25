# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, request, jsonify
from ..extensions import mongo, parser, jwt
from ..utils.decorator import check_permission
from ..utils.schema import UserSchema
from ..exception import BadRequest, NotFound
from ..db.mongo import MongoWrapper
import copy
import hashlib
from . import gen_id
from flask_babel import gettext
from marshmallow import fields
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_refresh_token_required, get_jwt_identity)


api = Blueprint('user_api', __name__, url_prefix='/api/v1/user')


@api.route('/register', methods=['POST'])
def register():
    schema = UserSchema()
    json_data = request.get_json()
    user, error = schema.load(json_data)
    if error:
        raise BadRequest(1007)
    user_collection = MongoWrapper(mongo, 'user')
    user_1 = user_collection.find_one(spec={'username': user['username']})
    if user_1:
        raise BadRequest(1008, ('username', user['username']))
    user_2 = user_collection.find_one({'email': user['email']})
    if user_2:
        raise BadRequest(1008, ('email', user['email']))
    new_user = copy.deepcopy(user)
    new_user['_id'] = gen_id('user')
    new_user['password'] = hashlib.md5(new_user['password']).hexdigest()
    user_collection.insert(**new_user)

    return jsonify({'message': gettext('REGISTER.SUCCESS')}), 200


@api.route('/login', methods=['POST'])
def login():
    params = {
        'username': fields.String(
            required=True,
            error_messages={'required': gettext('USERNAME.REQUIRED')}
        ),
        'password': fields.String(
            required=True,
            error_messages={'required': gettext('PASSWORD.REQUIRED')}
        )
    }
    args = parser.parse(params)
    username = args['username']
    password = args['password']
    password = hashlib.md5(password).hexdigest()
    user_collection = MongoWrapper(mongo, 'user')
    spec = {'$or': [{'username': username}, {'email': username}], 'password': password}
    user = user_collection.find_one(spec)
    if not user:
        raise NotFound(5001)
    else:
        user_obj = UserObj(user['username'], user['fullname'], user['phone_number'],
                           user['email'], user['status'], user['is_two_factor'], user['user_group'],
                           user['roles'])
        access_token = create_access_token(identity=user_obj, fresh=True)
        refresh_token = create_refresh_token(identity=user_obj)
        return jsonify({
            'access_token': access_token, 'refresh_token': refresh_token
        }), 200


@api.route('/edit', methods=['POST'])
@check_permission('manage_user')
def edit_user():
    schema = UserSchema()
    json_data = request.get_json()
    user, error = schema.load(json_data)
    _id = user['_id']
    user_collection = MongoWrapper(mongo, 'user')
    data = user_collection.find_one({'_id': _id})
    if not data:
        raise NotFound(5001)
    user_1 = user_collection.find_one(spec={'username': user['username']})
    if user_1:
        raise BadRequest(1008, ('username', user['username']))
    user_2 = user_collection.find_one({'email': user['email']})
    if user_2:
        raise BadRequest(1008, ('email', user['email']))
    user_collection.update({'_id': _id}, user)
    return jsonify({'message': gettext('USER.EDIT.SUCCESS')}), 200


@api.route('/refresh_token', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """
    Refresh token endpoint. This will generate a new access token from
    the refresh token, but will mark that access token as non-fresh,
    as we do not actually verify a password in this endpoint.
    :return:
    """
    current_user = get_jwt_identity()
    user_collection = MongoWrapper(mongo, 'user')
    spec = {'$or': [{'username': current_user}, {'email': current_user}]}
    user = user_collection.find_one(spec)
    if not user:
        raise NotFound(5001)
    else:
        user_obj = UserObj(user['username'], user['fullname'], user['phone_number'],
                           user['email'], user['status'], user['is_two_factor'], user['user_group'],
                           user['roles'])
        access_token = create_access_token(identity=user_obj, fresh=False)
        return jsonify({'access_token': access_token}), 200


@api.route('/refresh_login', methods=['POST'])
@jwt_refresh_token_required
def fresh_login():
    """
    Fresh login endpoint. This is designed to be used if we need to
    make a fresh token for a user (by verifying they have the
    correct username and password). Unlike the standard login endpoint,
    this will only return a new access token, so that we don't keep
    generating new refresh tokens, which entirely defeats their point.
    :return:
    """
    params = {
        'username': fields.String(
            required=True,
            error_messages={'required': gettext('USERNAME.REQUIRED')}
        ),
        'password': fields.String(
            required=True,
            error_messages={'required': gettext('PASSWORD.REQUIRED')}
        )
    }
    args = parser.parse(params)
    username = args['username']
    password = args['password']
    password = hashlib.md5(password).hexdigest()
    user_collection = MongoWrapper(mongo, 'user')
    spec = {'$or': [{'username': username}, {'email': username}], 'password': password}
    user = user_collection.find_one(spec)
    if not user:
        raise NotFound(5001)
    else:
        user_obj = UserObj(user['username'], user['fullname'], user['phone_number'],
                           user['email'], user['status'], user['is_two_factor'], user['user_group'],
                           user['roles'])
        new_token = create_access_token(identity=user_obj, fresh=True)
        return jsonify({'access_token': new_token}), 200


@jwt.user_claims_loader
def add_user_info_to_access_token(user):
    return {
        'roles': user.roles
    }


@jwt.user_identity_loader
def add_user_identity_to_access_token(user):
    return user.username


class UserObj(object):
    def __init__(self, username, fullname, phone_number,
                 email, status, is_two_factor, user_group, roles):
        self.username = username
        self.fullname = fullname
        self.phone_number = phone_number
        self.email = email
        self.status = status
        self.is_two_factor = is_two_factor
        self.user_group = user_group
        self.roles = roles

    def deserialize(self):
        return {'username': self.username, 'fullname': self.fullname, 'phone_number': self.phone_number,
                'email': self.email, 'status': self.status, 'is_two_factor': self.is_two_factor,
                'user_group': self.user_group, 'roles': self.roles}
