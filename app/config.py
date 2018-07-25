# -*- coding: utf-8 -*-
import os
import datetime

def make_dir(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    except Exception as e:
        raise e


class DefaultConfig(object):
    DEBUG = True
    FILE_NAME = __file__

    # Security
    # This is the secret key that is used for session signing.
    SECRET_KEY = os.urandom(24)

    # The filename for the info and error logs. The logfiles are stored at log-api/logs
    INFO_LOG = "info.log"
    ERROR_LOG = "error.log"
    current_path = os.path.dirname(__file__)
    LOG_FOLDER = os.path.join(os.path.abspath(os.path.dirname(current_path)), 'logs')

    MONGO_URI = "mongodb://127.0.0.1:27017/myDatabase"
    MONGO_HOST = '127.0.0.1'  # '$MONGODB_SERVER_IP'
    MONGO_PORT = 27017  # '$PORT': mặc định là 27017
    MONGO_DBNAME = ''  # $MONGODB_NAME'


class MyAPIConfig(DefaultConfig):
    JWT_SECRET_KEY = 'thild-' + os.urandom(24)
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = False
