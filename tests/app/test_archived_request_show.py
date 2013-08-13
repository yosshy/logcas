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


class ArchivedRequestShowTestCase(testing.TestCase):

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
                db.archived_logs.save({
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
        pass
    #db.archived_logs.drop()

    # no param

    def test_without_params(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    # page

    def test_with_page_(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", page=""))
        self.assert400(response)

    def test_with_page_abc(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", page="abc"))
        self.assert400(response)

    def test_with_page_0(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", page="0"))
        self.assert400(response)

    def test_with_page_1(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", page="1"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_page_100(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", page="100"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    # limit

    def test_with_limit_(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", limit=""))
        self.assert400(response)

    def test_with_limit_abc(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", limit="abc"))
        self.assert400(response)

    def test_with_limit_9(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", limit="9"))
        self.assert400(response)

    def test_with_limit_10(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", limit="10"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_limit_200(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", limit="200"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_limit_201(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", limit="201"))
        self.assert400(response)

    # levelno

    def test_with_levelno_(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno=""))
        self.assert400(response)

    def test_with_levelno_abc(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno="abc"))
        self.assert400(response)

    def test_with_levelno_0(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno="0"))
        self.assert400(response)

    def test_with_levelno_10(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno="10"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_levelno_20(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno="20"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_levelno_21(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno="21"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_levelno_30(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno="30"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_levelno_40(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno="40"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_levelno_50(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno="50"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_levelno_60(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", levelno="60"))
        self.assert400(response)

    # style

    def test_with_style_(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", style=""))
        self.assert400(response)

    def test_with_style_abc(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", style="abc"))
        self.assert400(response)

    def test_with_style_default(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", style="default"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_style_dark(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", style="dark"))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    # host

    def test_with_host_(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", host=""))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_host_20_characters(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", host="a" * 20))
        self.assert200(response)
        self.assertTemplateUsed('archived_request_show.html')

    def test_with_host_21_characters(self):
        response = self.client.get(url_for('_archived_request_show',
                                           request_id="10", host="a" * 21))
        self.assert400(response)


if __name__ == '__main__':
    unittest.main()
