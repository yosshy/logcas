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
from flask.ext.wtf import Form
from wtforms import validators
from wtforms import IntegerField, RadioField
import yaml

import pprint

TIMEZONE = tz.tzlocal()

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

ALLOWED_LEVELNO = [str(x) for x in LEVELMAP.keys()]
#ALLOWED_LEVELNO = LEVELMAP.keys()

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

# forms

class BasicForm(Form):
    page = IntegerField('Page', default=1,
                        validators=[validators.NumberRange(min=1)])
    limit = IntegerField('Limit', default=DEFAULT_LIMIT,
                         validators=[validators.NumberRange(min=10, max=200)])
    levelno = RadioField('Level', default=DEFAULT_LEVELNO, coerce=int,
                         choices=[(k, v) for k, v in LEVELMAP.iteritems()])
    created = IntegerField('Created', default=0,
                           validators=[validators.NumberRange(min=0)])
    span = IntegerField('Span', default=DEFAULT_SPAN,
                        validators=[validators.NumberRange(min=1, max=120)])


# controllers

@app.route('/')
def _index():
    return redirect(url_for('_request_index'))


@app.route('/requests')
def _request_index():
    forms = BasicForm(request.args)
    if not forms.validate():
        abort(400)
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    spec = {"extra.request_id": {"$exists": 1},
            "extra.user_id": {"$ne": None},
            "levelno": {"$gte": levelno}}
    counts, logs = get_grouped_logs(mongo.db.logs,
                                    spec=spec, page=page, limit=limit)
    pages = counts / limit + 1
    return render_template('request_index.html', **locals())


@app.route('/requests/<request_id>')
def _request_show(request_id):
    forms = BasicForm(request.args)
    if not forms.validate():
        abort(400)
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    spec = {'extra.request_id': request_id,
            'levelno': {'$gte': levelno}}
    counts, logs = get_logs(mongo.db.logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('request_show.html', **locals())


@app.route('/logs')
def _log_index():
    forms = BasicForm(request.args)
    if not forms.validate():
        abort(400)
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    created = forms.created.data
    span = forms.span.data
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
    forms = BasicForm(request.args)
    if not forms.validate():
        abort(400)
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    spec = {"extra.request_id": {"$exists": 1},
            "extra.user_id": {"$ne": None},
            "levelno": {"$gte": levelno}}
    counts, logs = get_grouped_logs(mongo.db.archived_logs,
                                    spec=spec, page=page, limit=limit)
    pages = counts / limit + 1
    return render_template('archived_request_index.html', **locals())


@app.route('/archived/requests/<request_id>')
def _archived_request_show(request_id):
    forms = BasicForm(request.args)
    if not forms.validate():
        abort(400)
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    spec = {'extra.request_id': request_id,
            'levelno': {'$gte': levelno}}
    counts, logs = get_logs(mongo.db.archived_logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('archived_request_show.html', **locals())


@app.route('/archived/logs')
def _archived_log_index():
    forms = BasicForm(request.args)
    if not forms.validate():
        abort(400)
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    created = forms.created.data
    span = forms.span.data
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
