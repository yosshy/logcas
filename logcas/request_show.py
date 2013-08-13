from flask import Flask
from flask import abort
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask.ext import pymongo
from flask.ext.wtf import Form
from wtforms import validators
from wtforms import IntegerField, RadioField, SelectField, TextField
import yaml

from logcas.bootstrap import *


# forms

class RequestShowForm(Form):
    page = IntegerField('Page', default=1,
                        validators=[validators.NumberRange(min=1)])
    limit = IntegerField('Limit', default=DEFAULT_LIMIT,
                         validators=[validators.NumberRange(min=10, max=200)])
    levelno = RadioField('Level', default=DEFAULT_LEVELNO, coerce=int,
                         choices=[(k, v) for k, v in sorted(LEVELMAP.items())])
    style = SelectField('Style', default=DEFAULT_STYLE,
                        choices=STYLEMAP)
    host = TextField('Host', default="",
                     validators=[validators.length(min=0, max=20)])


# controllers

@app.route('/requests/<request_id>')
def _request_show(request_id):
    forms = RequestShowForm(request.args)
    if not forms.validate():
        abort(400)
    style = forms.style.data
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    host = forms.host.data

    spec = {'extra.request_id': request_id,
            'levelno': {'$gte': levelno}}
    if len(host):
        spec.update({'hostname': host})
    counts, logs = get_logs(mongo.db.logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('request_show.html', **locals())


@app.route('/archived/requests/<request_id>')
def _archived_request_show(request_id):
    forms = RequestShowForm(request.args)
    if not forms.validate():
        abort(400)
    style = forms.style.data
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    host = forms.host.data

    spec = {'extra.request_id': request_id,
            'levelno': {'$gte': levelno}}
    if len(host):
        spec.update({'hostname': host})
    counts, logs = get_logs(mongo.db.archived_logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('archived_request_show.html', **locals())
