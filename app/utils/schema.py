# -*- coding: utf-8 -*-
from marshmallow import fields, Schema, validate, pre_load


class UserGroupSchema(Schema):
    _id = fields.String(dump_only=True)
    group_name = fields.String(required=True),
    description = fields.String(missing=''),
    roles = fields.List(fields.String(), default=[], required=True)


class UserSchema(Schema):
    _id = fields.String(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True,
                             validate=[validate.Length(min=6, max=36)],
                             load_only=True
                             )
    fullname = fields.String(missing=username)
    phone_number = fields.String()
    email = fields.String(required=True,
                          validate=validate.Email(error='Not a valid email address'))
    status = fields.Boolean(default=False, missing=False)
    is_two_factor = fields.Boolean(default=False, missing=False)
    user_group = fields.String(missing=None)
    roles = fields.List(fields.String(), missing=[], default=[])

    # Clean up data
    @pre_load
    def process_input(self, data):
        data['email'] = data['email'].lower().strip()
        return data


class RoleSchema(Schema):
    _id = fields.String()
    role_name = fields.String()
    description = fields.String()
    permission = fields.List(fields.String())


class PermissionSchema(Schema):
    _id = fields.String()
    permission_name = fields.String()
    description = fields.String()
