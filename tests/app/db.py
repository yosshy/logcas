from flask.ext import pymongo

import logcas.bootstrap
import logcas.log_index
import logcas.log_show
import logcas.request_index
import logcas.request_show

app = logcas.bootstrap.app
app.config['MONGO2_DBNAME'] = 'logcastest'
mongo = pymongo.PyMongo(app, config_prefix='MONGO2')
logcas.bootstrap.mongo = mongo
logcas.log_index.mongo = mongo
logcas.log_show.mongo = mongo
logcas.request_index.mongo = mongo
logcas.request_show.mongo = mongo

with app.app_context():
    logs = mongo.db.logs
    archived_logs = mongo.db.archived_logs
