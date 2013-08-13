from flask import abort
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.wtf import Form
from wtforms import validators
from wtforms import IntegerField, RadioField, SelectField, TextField

from logcas.bootstrap import *


# forms

class LogIndexForm(Form):
    page = IntegerField('Page', default=1,
                        validators=[validators.NumberRange(min=1)])
    limit = IntegerField('Limit', default=DEFAULT_LIMIT,
                         validators=[validators.NumberRange(min=10, max=200)])
    levelno = RadioField('Level', default=DEFAULT_LEVELNO, coerce=int,
                         choices=[(k, v) for k, v in sorted(LEVELMAP.items())])
    created = IntegerField('Created', default=0,
                           validators=[validators.NumberRange(min=0)])
    span = IntegerField('Span', default=DEFAULT_SPAN,
                        validators=[validators.NumberRange(min=1, max=120)])
    style = SelectField('Style', default=DEFAULT_STYLE,
                        choices=STYLEMAP)
    host = TextField('Host', default="",
                     validators=[validators.length(min=0, max=20)])


# controllers

@app.route('/logs')
def _log_index():
    forms = LogIndexForm(request.args)
    if not forms.validate():
        abort(400)
    style = forms.style.data
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    created = forms.created.data
    span = forms.span.data
    host = forms.host.data

    spec = {'levelno': {'$gte': levelno}}
    if created:
        spec.update({
            'created': {"$gte": created - span, "$lte": created + span},
        })
    if len(host):
        spec.update({'hostname': host})
    counts, logs = get_logs(mongo.db.logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('log_index.html', **locals())


@app.route('/archived/logs')
def _archived_log_index():
    forms = LogIndexForm(request.args)
    if not forms.validate():
        abort(400)
    style = forms.style.data
    page = forms.page.data
    limit = forms.limit.data
    levelno = forms.levelno.data
    created = forms.created.data
    span = forms.span.data
    host = forms.host.data

    spec = {'levelno': {'$gte': levelno}}
    if created:
        spec.update({
            'created': {"$gte": created - span, "$lte": created + span},
        })
    if len(host):
        spec.update({'hostname': host})
    counts, logs = get_logs(mongo.db.archived_logs,
                            spec=spec, limit=limit, page=page)
    pages = counts / limit + 1
    return render_template('archived_log_index.html', **locals())
