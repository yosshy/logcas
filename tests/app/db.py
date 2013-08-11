from flask.ext import pymongo

import logcas.app


app = logcas.app.app
app.config['MONGO2_DBNAME'] = 'logcastest'
logcas.app.mongo = pymongo.PyMongo(app, config_prefix='MONGO2')
with app.app_context():
    logs = logcas.app.mongo.db.logs
    archived_logs = logcas.app.mongo.db.archived_logs
