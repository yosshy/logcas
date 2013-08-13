from datetime import datetime
from datetime import timedelta
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL
import unittest

from bson.objectid import ObjectId
from pymongo import MongoClient

import logcas.bootstrap
from tools.archiver import reset_archived_flag

AUDIT = INFO + 1


MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "logcastest"
LOG_COLLECTION = "logs"

reset_archived_flag.MONGO_DB = MONGO_DB

# Prepare MongoDB client instance.
client = MongoClient(MONGO_HOST, MONGO_PORT)

# Log database object in MongoDB.
db = client[MONGO_DB]
odb = db.logs


class ResetArchivedFlasTestCase(unittest.TestCase):

    def _save_dummy(self, now, level, request_id, archived):
        dummy_doc = {
            "archived": archived,
            "time": now,
            "created": int(now.strftime("%s")),
            "message": "This is a message",
            "hostname": "localhost",
            "levelno": level,
            "levelname": logcas.bootstrap.LEVELMAP[level],
            "binary": "nova-compute",
            "extra": {
                "request_id": request_id,
                "remote_address": "127.0.0.1",
                "project_name": "testproject",
                "user_name": "testuser",
            }
        }
        odb.save(dummy_doc)

    @classmethod
    def setUpClass(cls):
        odb.drop()

    def tearDown(self):
        odb.drop()

    # no logs
    def test_without_log(self):
        reset_archived_flag.main()
        self.assertEqual(0, odb.find().count())

    # no archived logs
    def test_without_failed_logs(self):
        now = datetime.today()
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            for level in [DEBUG, INFO, AUDIT]:
                self._save_dummy(now, level, str(i), False)
                now = now + onesecond
        self.assertEqual(0, odb.find({"archived": True}).count())
        reset_archived_flag.main()
        self.assertEqual(0, odb.find({"archived": True}).count())

    # some archived logs
    def test_with_many_failed_logs_without_request_id(self):
        now = datetime.today()
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            self._save_dummy(now, ERROR, None, True)
            now = now + onesecond
        for i in range(0, 20):
            self._save_dummy(now, ERROR, None, False)
            now = now + onesecond
        self.assertEqual(20, odb.find({"archived": True}).count())
        reset_archived_flag.main()
        self.assertEqual(0, odb.find({"archived": True}).count())

if __name__ == '__main__':
    unittest.main()
