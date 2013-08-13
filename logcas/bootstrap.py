import logging

from flask import Flask
from flask.ext import pymongo
import yaml


ASC = pymongo.ASCENDING
DESC = pymongo.DESCENDING
DEFAULT_ORDER = ASC

MONGO_DBNAME = 'logcas'
#MONGO_HOST = 'localhost'
#MONGO_PORT = '27017'
#MONGO_USERNAME = 'foo'
#MONGO_PASSWORD = 'bar'

SECRET_KEY = 'secrete'
CSRF_ENABLED = False

app = Flask(__name__)
app.config.from_object(__name__)

mongo = pymongo.PyMongo(app)

yaml.add_representer(unicode, lambda dumper, value: dumper.represent_scalar(
    u'tag:yaml.org,2002:str', value))

DEFAULT_COLUMNS = {
    'time',
    'created',
    'message',
    'hostname',
    'levelname',
    'binary',
    'extra.request_id',
    'extra.remote_address',
    'extra.project_name',
    'extra.user_name',
}

LEVELMAP = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.INFO + 1: "AUDIT",
    logging.WARN: "WARN",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
}

STYLEMAP = [
    ("default", "Default"),
    ("dark", "Dark"),
]

DEFAULT_LEVELNO = logging.INFO
DEFAULT_LIMIT = 100
DEFAULT_SPAN = 10
DEFAULT_STYLE = "default"


def columns_to_fields(columns=[]):
    result = {}
    for column in columns:
        result[column] = 1
    return result


def get_logs(col, spec={}, columns=DEFAULT_COLUMNS,
             page=1, limit=DEFAULT_LIMIT):
    fields = columns_to_fields(columns)
    logs = col.find(
        spec=spec,
        fields=fields,
        sort=[('_id', DEFAULT_ORDER)],
        limit=limit,
        skip=(page - 1) * limit)
    return logs.count(), logs


def get_grouped_logs(col, spec={}, page=1, limit=DEFAULT_LIMIT):
    logs = col.aggregate([
        {"$match": spec},
        {"$group": {
            "_id": "$extra.request_id",
            "count": {"$sum": 1},
            "project_name": {"$first": "$extra.project_name"},
            "user_name": {"$first": "$extra.user_name"},
            "remote_address": {"$first": "$extra.remote_address"},
            "maxlevelno": {"$max": "$levelno"},
            "starttime": {"$min": "$time"},
            "endtime": {"$max": "$time"},
        }},
        {"$sort": {'starttime': DEFAULT_ORDER}},
    ])['result']
    start = (page - 1) * limit
    last = page * limit
    new_logs = logs[start:last]
    for log in new_logs:
        log['levelname'] = LEVELMAP.get(log['maxlevelno'], '')
    return len(logs), new_logs
