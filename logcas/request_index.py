from flask import abort
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask.ext.wtf import Form
from wtforms import validators
from wtforms import IntegerField, RadioField, SelectField, TextField
import yaml

from logcas.bootstrap import *

# forms

class RequestIndexForm(Form):
    page = IntegerField('Page', default=1,
                        validators=[validators.NumberRange(min=1)])
    limit = IntegerField('Limit', default=DEFAULT_LIMIT,
                         validators=[validators.NumberRange(min=10, max=200)])
    levelno = RadioField('Level', default=DEFAULT_LEVELNO, coerce=int,
                         choices=[(k, v) for k, v in sorted(LEVELMAP.items())])
    style = SelectField('Style', default=DEFAULT_STYLE,
                        choices=STYLEMAP)


# controllers


@app.route('/')
def _index():
    return redirect(url_for('_request_index'))


@app.route('/requests')
def _request_index():
    forms = RequestIndexForm(request.args)
    if not forms.validate():
        abort(400)
    style = forms.style.data
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


@app.route('/archived/requests')
def _archived_request_index():
    forms = RequestIndexForm(request.args)
    if not forms.validate():
        abort(400)
    style = forms.style.data
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
