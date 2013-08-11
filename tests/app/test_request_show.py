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


class RequestShowTestCase(testing.TestCase):

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
                db.logs.save({
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
        db.logs.drop()

    # no param

    def test_request_show_without_params(self):
        response = self.client.get(url_for('_request_show', request_id="0"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    # page

    def test_request_show_with_page_(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", page=""))
        self.assert400(response)

    def test_request_show_with_page_abc(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", page="abc"))
        self.assert400(response)

    def test_request_show_with_page_0(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", page="0"))
        self.assert400(response)

    def test_request_show_with_page_1(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", page="1"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    def test_request_show_with_page_100(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", page="100"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    # limit

    def test_request_show_with_limit_(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", limit=""))
        self.assert400(response)

    def test_request_show_with_limit_abc(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", limit="abc"))
        self.assert400(response)

    def test_request_show_with_limit_9(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", limit="9"))
        self.assert400(response)

    def test_request_show_with_limit_10(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", limit="10"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    def test_request_show_with_limit_200(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", limit="200"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    def test_request_show_with_limit_201(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", limit="201"))
        self.assert400(response)

    # levelno

    def test_request_show_with_levelno_(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno=""))
        self.assert400(response)

    def test_request_show_with_levelno_abc(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno="abc"))
        self.assert400(response)

    def test_request_show_with_levelno_0(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno="0"))
        self.assert400(response)

    def test_request_show_with_levelno_10(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno="10"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    def test_request_show_with_levelno_20(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno="20"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    def test_request_show_with_levelno_21(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno="21"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    def test_request_show_with_levelno_30(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno="30"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    def test_request_show_with_levelno_40(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno="40"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    def test_request_show_with_levelno_50(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno="50"))
        self.assert200(response)
        self.assertTemplateUsed('request_show.html')

    def test_request_show_with_levelno_60(self):
        response = self.client.get(url_for('_request_show',
                                           request_id="0", levelno="60"))
        self.assert400(response)


if __name__ == '__main__':
    unittest.main()
