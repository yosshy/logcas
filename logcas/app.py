import logging

from flask import Flask
from flask import abort
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask.ext import pymongo
import yaml


ASC = pymongo.ASCENDING
DESC = pymongo.DESCENDING
DEFAULT_ORDER = ASC

#MONGO_DBNAME = 'fluentd'
MONGO_DBNAME = 'archive'
#MONGO_HOST = 'localhost'
#MONGO_PORT = '27017'
#MONGO_USERNAME = 'foo'
#MONGO_PASSWORD = 'bar'


app = Flask(__name__)
app.config.from_object(__name__)

mongo = pymongo.PyMongo(app)
yaml.add_representer(unicode, lambda dumper, value: dumper.represent_scalar(
    u'tag:yaml.org,2002:str', value))

DEFAULT_COLUMNS = {
    'time',
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


def get_grouped_logs(spec={}, page=1, limit=DEFAULT_LIMIT,
                     order=DEFAULT_ORDER):

    if page < 1:
        abort(400)
    if order not in [ASC, DESC]:
        abort(400)
    logs = mongo.db.logs.aggregate([
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
        {"$sort": {'starttime': order}},
    ])['result']
    start = (page - 1) * limit
    last = page * limit
    new_logs = logs[start:last]
    for log in new_logs:
        log['levelname'] = LEVELMAP.get(log['maxlevelno'], '')
    return len(logs), new_logs


@app.route('/')
def _index():
    return redirect(url_for('_request_index'))


@app.route('/requests')
def _request_index():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    levelno = int(request.args.get('levelno', DEFAULT_LEVELNO))
    spec = {"extra.request_id": {"$exists": 1},
            "extra.user_id": {"$ne": None},
            "levelno": {"$gte": levelno}}
    counts, logs = get_grouped_logs(spec=spec, page=page, limit=limit)
    pages = counts / limit + 1
    return render_template('request_index.html', **locals())


@app.route('/requests/<request_id>')
def _request_show(request_id):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    levelno = int(request.args.get('levelno', DEFAULT_LEVELNO))
    spec = {'extra.request_id': request_id,
            'levelno': {'$gte': levelno}}
    counts, logs = get_logs(spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('request_show.html', **locals())


@app.route('/logs')
def _log_index():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    levelno = int(request.args.get('levelno', DEFAULT_LEVELNO))
    spec = {'levelno': {'$gte': levelno},
            'extra.request_id': {'$exists': 1}}
    counts, logs = get_logs(spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('log_index.html', **locals())


@app.route('/logs/<ObjectId:log_id>')
def _log_show(log_id):
    spec = {'_id': log_id}
    log = mongo.db.logs.find_one_or_404(spec)
    log.pop('_id')
    log_yaml = yaml.dump(log, width=200, default_flow_style=False)
    return render_template('log_show.html', **locals())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
