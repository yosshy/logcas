from datetime import datetime
from datetime import timedelta
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL
import unittest

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
import mox

from tools.archiver import archiver
import logcas.bootstrap

AUDIT = INFO + 1


MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "logcastest"
LOG_COLLECTION = "logs"
ARCHIVE_COLLECTION = "archived_logs"
ARCHIVE_SIZE = 50 * 1024 * 1024

archiver.MONGO_DB = MONGO_DB

# Prepare MongoDB client instance.
client = MongoClient(MONGO_HOST, MONGO_PORT)

# Log database object in MongoDB.
db = client[MONGO_DB]
odb = db.logs
adb = db.archived_logs


class ArchiverTestCase(unittest.TestCase):

    def _save_dummy(self, now, level, request_id):
        dummy_doc = {
            "archived": False,
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
        adb.drop()

    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        odb.drop()
        adb.drop()
        self.mox.VerifyAll()
        self.mox.UnsetStubs()

    # no logs
    def test_without_log(self):
        archiver.main()
        self.assertEqual(0, adb.find().count())

    # no failed logs
    def test_without_failed_logs(self):
        now = datetime.today()
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            for level in [DEBUG, INFO, AUDIT]:
                self._save_dummy(now, level, str(i))
                now = now + onesecond
        archiver.main()
        self.assertEqual(0, adb.find().count())

    # many failed logs without request_id
    def test_with_many_failed_logs_without_request_id(self):
        now = datetime.today()
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            self._save_dummy(now, ERROR, None)
            now = now + onesecond
        archiver.main()
        self.assertEqual(20, adb.find().count())

    # many failed logs
    def test_with_many_failed_logs(self):
        now = datetime.today()
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            for level in [DEBUG, INFO, AUDIT, WARN, ERROR, CRITICAL]:
                self._save_dummy(now, level, str(i))
                now = now + onesecond
        archiver.main()
        self.assertEqual(20 * 6, adb.find().count())

    # many logs with failed one.
    def test_with_many_logs_and_failed_one(self):
        now = datetime.today()
        self._save_dummy(now, ERROR, None)
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            for level in [DEBUG, INFO, AUDIT]:
                self._save_dummy(now, level, str(i))
                now = now + onesecond
        archiver.main()
        # 4 = 3 logs (DEBUG, INFO, AUDIT) + 1 log (ERROR)
        self.assertEqual(4, adb.find().count())

    # many logs with failed one and exceptions #1.
    def test_with_many_logs_and_failed_one_with_exceptions_1(self):
        now = datetime.today()
        self._save_dummy(now, ERROR, None)
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            for level in [DEBUG, INFO, AUDIT]:
                self._save_dummy(now, level, str(i))
                now = now + onesecond
        self.mox.StubOutWithMock(Collection, 'save')
        Collection.save(mox.IgnoreArg()).AndRaise(Exception())
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndRaise(Exception())
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        self.mox.ReplayAll()
        archiver.main()

    # many logs with failed one and exceptions #2.
    def test_with_many_logs_and_failed_one_with_exceptions_2(self):
        now = datetime.today()
        self._save_dummy(now, ERROR, None)
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            for level in [DEBUG, INFO, AUDIT]:
                self._save_dummy(now, level, str(i))
                now = now + onesecond
        self.mox.StubOutWithMock(Collection, 'save')
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndRaise(Exception())
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndRaise(Exception())
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        Collection.save(mox.IgnoreArg()).AndReturn(None)
        self.mox.ReplayAll()
        archiver.main()

if __name__ == '__main__':
    unittest.main()
