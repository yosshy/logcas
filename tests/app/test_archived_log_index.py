from datetime import datetime
from datetime import timedelta
import json
import unittest

from bson.objectid import ObjectId
from flask import url_for
from flask.ext import testing
from flask.ext import pymongo

import logcas.app
import db


class ArchivedLogIndexTestCase(testing.TestCase):

    def create_app(self):
        app = logcas.app.app
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        return app

    @classmethod
    def setUpClass(cls):
        now = datetime.today()
        cls.now = now
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            for level in logcas.app.LEVELMAP.keys():
                db.archived_logs.save({
                    "time": now,
                    "created": int(now.strftime("%s")),
                    "message": "This is a message",
                    "hostname": "localhost",
                    "levelname": logcas.app.LEVELMAP[level],
                    "binary": "nova-compute",
                    "extra": {
                        "request_id": str(i),
                        "remote_address": "127.0.0.1",
                        "project_name": "testproject",
                        "user_name": "testuser",
                    }
                })
                now = now + onesecond

    @classmethod
    def tearDownClass(cls):
        db.archived_logs.drop()

    # no param

    def test_without_params(self):
        response = self.client.get(url_for('_archived_log_index'))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    # page

    def test_with_page_(self):
        response = self.client.get(url_for('_archived_log_index',
                                           page=""))
        self.assert400(response)

    def test_with_page_abc(self):
        response = self.client.get(url_for('_archived_log_index',
                                           page="abc"))
        self.assert400(response)

    def test_with_page_0(self):
        response = self.client.get(url_for('_archived_log_index',
                                           page="0"))
        self.assert400(response)

    def test_with_page_1(self):
        response = self.client.get(url_for('_archived_log_index',
                                           page="1"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_page_100(self):
        response = self.client.get(url_for('_archived_log_index',
                                           page="100"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    # limit

    def test_with_limit_(self):
        response = self.client.get(url_for('_archived_log_index',
                                           limit=""))
        self.assert400(response)

    def test_with_limit_abc(self):
        response = self.client.get(url_for('_archived_log_index',
                                           limit="abc"))
        self.assert400(response)

    def test_with_limit_9(self):
        response = self.client.get(url_for('_archived_log_index',
                                           limit="9"))
        self.assert400(response)

    def test_with_limit_10(self):
        response = self.client.get(url_for('_archived_log_index',
                                           limit="10"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_limit_200(self):
        response = self.client.get(url_for('_archived_log_index',
                                           limit="200"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_limit_201(self):
        response = self.client.get(url_for('_archived_log_index',
                                           limit="201"))
        self.assert400(response)

    # levelno

    def test_with_levelno_(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno=""))
        self.assert400(response)

    def test_with_levelno_abc(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno="abc"))
        self.assert400(response)

    def test_with_levelno_0(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno="0"))
        self.assert400(response)

    def test_with_levelno_10(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno="10"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_levelno_20(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno="20"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_levelno_21(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno="21"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_levelno_30(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno="30"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_levelno_40(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno="40"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_levelno_50(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno="50"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_levelno_60(self):
        response = self.client.get(url_for('_archived_log_index',
                                           levelno="60"))
        self.assert400(response)

    # created

    def test_with_created_(self):
        response = self.client.get(url_for('_archived_log_index',
                                           created=""))
        self.assert400(response)

    def test_with_created_abc(self):
        response = self.client.get(url_for('_archived_log_index',
                                           created="abc"))
        self.assert400(response)

    def test_with_created_minus(self):
        response = self.client.get(url_for('_archived_log_index',
                                           created="-1"))
        self.assert400(response)

    def test_with_created_0(self):
        response = self.client.get(url_for('_archived_log_index',
                                           created="0"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_created_now(self):
        now = datetime.today().strftime("%s")
        response = self.client.get(url_for('_archived_log_index',
                                           created=str(now)))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    # span

    def test_with_span_(self):
        response = self.client.get(url_for('_archived_log_index',
                                           span=""))
        self.assert400(response)

    def test_with_span_abc(self):
        response = self.client.get(url_for('_archived_log_index',
                                           span="abc"))
        self.assert400(response)

    def test_with_span_0(self):
        response = self.client.get(url_for('_archived_log_index',
                                           span="0"))
        self.assert400(response)

    def test_with_span_1(self):
        response = self.client.get(url_for('_archived_log_index',
                                           span="1"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_span_120(self):
        response = self.client.get(url_for('_archived_log_index',
                                           span="120"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_span_121(self):
        response = self.client.get(url_for('_archived_log_index',
                                           span="121"))
        self.assert400(response)

    # style

    def test_with_style_(self):
        response = self.client.get(url_for('_archived_log_index',
                                           style=""))
        self.assert400(response)

    def test_with_style_abc(self):
        response = self.client.get(url_for('_archived_log_index',
                                           style="abc"))
        self.assert400(response)

    def test_with_style_default(self):
        response = self.client.get(url_for('_archived_log_index',
                                           style="default"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')

    def test_with_style_dark(self):
        response = self.client.get(url_for('_archived_log_index',
                                           style="dark"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_index.html')


if __name__ == '__main__':
    unittest.main()
