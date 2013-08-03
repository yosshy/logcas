import logging

from flask import Flask
from flask import abort
from flask import render_template
from flask import request
from flask.ext import pymongo


ASC = pymongo.ASCENDING
DESC = pymongo.DESCENDING
DEFAULT_ORDER = ASC

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'fluentd'
#app.config['MONGO_HOST'] = 'localhost'
#app.config['MONGO_PORT'] = '27017'
#app.config['MONGO_USERNAME'] = 'foo'
#app.config['MONGO_PASSWORD'] = 'bar'

mongo = pymongo.PyMongo(app)

DEFAULT_COLUMNS = {
    'time',
    'message',
    'hostname',
    'levelname',
    'binary',
    'request_id',
    'remote_address',
    'tenant',
    'user_name',
}

LEVELMAP = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.INFO + 1: "AUDIT",
    logging.WARN: "WARN",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
}

DEFAULT_LEVELNO = logging.INFO
DEFAULT_LIMIT = 100

def columns_to_fields(columns=[]):
    result = {}
    for column in columns:
        result[column] = 1
    return result

def get_logs(spec={}, columns=DEFAULT_COLUMNS,
             page=1, limit=DEFAULT_LIMIT, order=DEFAULT_ORDER):
    if page < 1:
        abort(400)
    if order not in [ASC, DESC]:
        abort(400)
    fields = columns_to_fields(columns)
    logs = mongo.db.logs.find(
                        spec=spec,
                        fields=fields,
                        sort=[('_id', order)],
                        limit=limit,
                        skip=(page - 1) * limit)
    return logs.count(), logs

def get_grouped_logs(page=1, limit=DEFAULT_LIMIT, order=DEFAULT_ORDER):
    if page < 1:
        abort(400)
    if order not in [ASC, DESC]:
        abort(400)
    logs = mongo.db.logs.aggregate([
        {"$match": {
            "request_id": {"$exists": 1},
            "levelno": {"$gt": 10}
        }},
        {"$group": {
            "_id": "$request_id",
            "project_name": {"$first": "$project_name"},
            "user_name": {"$first": "$user_name"},
            "remote_address": {"$first": "$remote_address"},
            "maxlevelno": {"$max": "$levelno"},
            "starttime": {"$min": "$time"},
            "endtime": {"$max": "$time"},
        }},
        {"$sort": {'starttime': order}},
        ])['result']
    start = (page - 1) * limit
    last = page * limit
    new_logs = logs[start:last]
    for log in new_logs:
        log['levelname'] = LEVELMAP.get(log['maxlevelno'],'')
    return len(logs), new_logs

@app.route('/')
def _index():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    spec = {'levelno': {'$gte': DEFAULT_LEVELNO},
            'request_id': {'$exists': 1}}
    counts, logs = get_logs(spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('index.html', **locals())

@app.route('/errors')
def _errors():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    spec={'levelno': {'$gte': logging.ERROR}}
    counts, logs = get_logs(spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('index.html', **locals())

@app.route('/warnings')
def _warnings():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    spec={'levelno': {'$gte': logging.ERROR}}
    counts, logs = get_logs(spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('index.html', **locals())

@app.route('/requests')
def _requests_index():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    counts, logs = get_grouped_logs(page=page, limit=limit)
    pages = counts / limit + 1
    return render_template('request_index.html', **locals())

@app.route('/requests/<request_id>')
def _requests_show(request_id):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    spec = {'request_id': request_id}
    counts, logs = get_logs(spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('request_show.html', **locals())

if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=True)
