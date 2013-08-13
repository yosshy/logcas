from flask import abort
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.wtf import Form
from wtforms import validators
from wtforms import IntegerField, RadioField, SelectField, TextField

from logcas.bootstrap import *


# forms

class LogShowForm(Form):
    style = SelectField('Style', default=DEFAULT_STYLE,
                                    choices=STYLEMAP)

# controllers

@app.route('/logs/<ObjectId:log_id>')
def _log_show(log_id):
    forms = LogShowForm(request.args)
    if not forms.validate():
        abort(400)
    style = forms.style.data

    spec = {'_id': log_id}
    log = mongo.db.logs.find_one_or_404(spec)
    log.pop('_id')
    log_yaml = yaml.dump(log, width=200, default_flow_style=False)
    return render_template('log_show.html', **locals())


@app.route('/archived/logs/<ObjectId:log_id>')
def _archived_log_show(log_id):
    forms = LogShowForm(request.args)
    if not forms.validate():
        abort(400)
    style = forms.style.data

    spec = {'_id': log_id}
    log = mongo.db.archived_logs.find_one_or_404(spec)
    log.pop('_id')
    log_yaml = yaml.dump(log, width=200, default_flow_style=False)
    return render_template('archived_log_show.html', **locals())
