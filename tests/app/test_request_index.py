from datetime import datetime
from datetime import timedelta
import json
import unittest

from bson.objectid import ObjectId
from flask import url_for
from flask.ext import testing
from flask.ext import pymongo

import logcas.bootstrap
import db


class IndexTestCase(testing.TestCase):

    def create_app(self):
        app = logcas.bootstrap.app
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        return app

    def test_index(self):
        response = self.client.get('/')
        self.assertRedirects(response, url_for('_request_index'))


class RequestIndexTestCase(testing.TestCase):

    col = db.logs
    controller = '_request_index'
    template = 'request_index.html'

    def create_app(self):
        app = logcas.bootstrap.app
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        return app

    @classmethod
    def setUpClass(cls):
        now = datetime.today()
        cls.now = now
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            for level in logcas.bootstrap.LEVELMAP.keys():
                cls.col.save({
                    "time": now,
                    "created": int(now.strftime("%s")),
                    "message": "This is a message",
                    "hostname": "localhost",
                    "levelno": level,
                    "levelname": logcas.bootstrap.LEVELMAP[level],
                    "binary": "nova-compute",
                    "extra": {
                        "request_id": str(i),
                        "remote_address": "127.0.0.1",
                        "project_name": "testproject",
                        "user_name": "testuser",
                        "user_id": "xxxxxxxx",
                    }
                })
                now = now + onesecond

    @classmethod
    def tearDownClass(cls):
        cls.col.drop()

    # no param

    def test_without_params(self):
        response = self.client.get(url_for(self.controller))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    # page

    def test_with_page_(self):
        response = self.client.get(url_for(self.controller, page=""))
        self.assert400(response)

    def test_with_page_abc(self):
        response = self.client.get(url_for(self.controller, page="abc"))
        self.assert400(response)

    def test_with_page_0(self):
        response = self.client.get(url_for(self.controller, page="0"))
        self.assert400(response)

    def test_with_page_1(self):
        response = self.client.get(url_for(self.controller, page="1"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_page_100(self):
        response = self.client.get(url_for(self.controller, page="100"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    # limit

    def test_with_limit_(self):
        response = self.client.get(url_for(self.controller, limit=""))
        self.assert400(response)

    def test_with_limit_abc(self):
        response = self.client.get(url_for(self.controller, limit="abc"))
        self.assert400(response)

    def test_with_limit_9(self):
        response = self.client.get(url_for(self.controller, limit="9"))
        self.assert400(response)

    def test_with_limit_10(self):
        response = self.client.get(url_for(self.controller, limit="10"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_limit_200(self):
        response = self.client.get(url_for(self.controller, limit="200"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_limit_201(self):
        response = self.client.get(url_for(self.controller, limit="201"))
        self.assert400(response)

    # levelno

    def test_with_levelno_(self):
        response = self.client.get(url_for(self.controller, levelno=""))
        self.assert400(response)

    def test_with_levelno_abc(self):
        response = self.client.get(url_for(self.controller, levelno="abc"))
        self.assert400(response)

    def test_with_levelno_0(self):
        response = self.client.get(url_for(self.controller, levelno="0"))
        self.assert400(response)

    def test_with_levelno_10(self):
        response = self.client.get(url_for(self.controller, levelno="10"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_levelno_20(self):
        response = self.client.get(url_for(self.controller, levelno="20"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_levelno_21(self):
        response = self.client.get(url_for(self.controller, levelno="21"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_levelno_30(self):
        response = self.client.get(url_for(self.controller, levelno="30"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_levelno_40(self):
        response = self.client.get(url_for(self.controller, levelno="40"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_levelno_50(self):
        response = self.client.get(url_for(self.controller, levelno="50"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_levelno_60(self):
        response = self.client.get(url_for(self.controller, levelno="60"))
        self.assert400(response)

    # style

    def test_with_style_(self):
        response = self.client.get(url_for(self.controller, style=""))
        self.assert400(response)

    def test_with_style_abc(self):
        response = self.client.get(url_for(self.controller, style="abc"))
        self.assert400(response)

    def test_with_style_default(self):
        response = self.client.get(url_for(self.controller, style="default"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)

    def test_with_style_dark(self):
        response = self.client.get(url_for(self.controller, style="dark"))
        self.assert200(response)
        self.assertTemplateUsed(self.template)


class ArchivedRequestIndexTestCase(RequestIndexTestCase):

    col = db.archived_logs
    controller = '_archived_request_index'
    template = 'archived_request_index.html'


if __name__ == '__main__':
    unittest.main()
