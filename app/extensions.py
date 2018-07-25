# -*- coding: utf-8 -*-
from flask_pymongo import PyMongo
from webargs.flaskparser import FlaskParser
from flask_jwt_extended import JWTManager

mongo = PyMongo()
jwt = JWTManager()
parser = FlaskParser()

