import logging
from datetime import datetime
from dateutil import tz
import time

from flask import Flask
from flask import abort
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask.ext import pymongo
import yaml

import apiform

TIMEZONE = tz.tzlocal()

ASC = pymongo.ASCENDING
DESC = pymongo.DESCENDING
DEFAULT_ORDER = ASC

MONGO_DBNAME = 'logcas'
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

ALLOWED_LEVELNO = [str(x) for x in LEVELMAP.keys()]

DEFAULT_LEVELNO = logging.INFO
DEFAULT_LIMIT = 100
DEFAULT_SPAN = 10


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


@app.template_filter('localtime')
def _localtime_filter(dtime):
    return dtime.replace(microsecond=0, tzinfo=None)


@app.template_filter('unixtime')
def _unixtime_filter(dtime):
    return int(time.mktime(dtime.timetuple()))


class Validator(apiform.Form):
    page = apiform.IntField(min=1, default=1)
    limit = apiform.IntField(min=10, max=200, default=DEFAULT_LIMIT)
    levelno = apiform.IntField(allowed=ALLOWED_LEVELNO,
                               default=DEFAULT_LEVELNO)
    created = apiform.IntField(required=False, min=0, default=0)
    span = apiform.IntField(min=1, max=120, default=DEFAULT_SPAN)


@app.route('/')
def _index():
    return redirect(url_for('_request_index'))


@app.route('/requests')
def _request_index():
    form = Validator(request)
    if not form.validate():
        abort(400)
    page = form.get('page')
    limit = form.get('limit')
    levelno = form.get('levelno')
    spec = {"extra.request_id": {"$exists": 1},
            "extra.user_id": {"$ne": None},
            "levelno": {"$gte": levelno}}
    counts, logs = get_grouped_logs(mongo.db.logs,
                                    spec=spec, page=page, limit=limit)
    pages = counts / limit + 1
    return render_template('request_index.html', **locals())


@app.route('/requests/<request_id>')
def _request_show(request_id):
    form = Validator(request)
    if not form.validate():
        abort(400)
    page = form.get('page')
    limit = form.get('limit')
    levelno = form.get('levelno')
    spec = {'extra.request_id': request_id,
            'levelno': {'$gte': levelno}}
    counts, logs = get_logs(mongo.db.logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('request_show.html', **locals())


@app.route('/logs')
def _log_index():
    form = Validator(request)
    if not form.validate():
        abort(400)
    page = form.get('page')
    limit = form.get('limit')
    levelno = form.get('levelno')
    created = form.get('created')
    span = form.get('span')
    spec = {'levelno': {'$gte': levelno}}
    if created:
        spec.update({
            'created': {"$gte": created - span, "$lte": created + span},
        })
    counts, logs = get_logs(mongo.db.logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('log_index.html', **locals())


@app.route('/logs/<ObjectId:log_id>')
def _log_show(log_id):
    spec = {'_id': log_id}
    log = mongo.db.logs.find_one_or_404(spec)
    log.pop('_id')
    log_yaml = yaml.dump(log, width=200, default_flow_style=False)
    return render_template('log_show.html', **locals())


@app.route('/archived/requests')
def _archived_request_index():
    form = Validator(request)
    if not form.validate():
        abort(400)
    page = form.get('page')
    limit = form.get('limit')
    levelno = form.get('levelno')
    spec = {"extra.request_id": {"$exists": 1},
            "extra.user_id": {"$ne": None},
            "levelno": {"$gte": levelno}}
    counts, logs = get_grouped_logs(mongo.db.archived_logs,
                                    spec=spec, page=page, limit=limit)
    pages = counts / limit + 1
    return render_template('archived_request_index.html', **locals())


@app.route('/archived/requests/<request_id>')
def _archived_request_show(request_id):
    form = Validator(request)
    if not form.validate():
        abort(400)
    page = form.get('page')
    limit = form.get('limit')
    levelno = form.get('levelno')
    spec = {'extra.request_id': request_id,
            'levelno': {'$gte': levelno}}
    counts, logs = get_logs(mongo.db.archived_logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('archived_request_show.html', **locals())


@app.route('/archived/logs')
def _archived_log_index():
    form = Validator(request)
    if not form.validate():
        abort(400)
    page = form.get('page')
    limit = form.get('limit')
    levelno = form.get('levelno')
    created = form.get('created')
    span = form.get('span')
    spec = {'levelno': {'$gte': levelno}}
    if created:
        spec.update({
            'created': {"$gte": created - span, "$lte": created + span},
        })
    counts, logs = get_logs(mongo.db.archived_logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('archived_log_index.html', **locals())


@app.route('/archived/logs/<ObjectId:log_id>')
def _archived_log_show(log_id):
    spec = {'_id': log_id}
    log = mongo.db.archived_logs.find_one_or_404(spec)
    log.pop('_id')
    log_yaml = yaml.dump(log, width=200, default_flow_style=False)
    return render_template('archived_log_show.html', **locals())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
