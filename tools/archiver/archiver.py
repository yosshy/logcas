#!/usr/bin/python
import logging
import sys

from pymongo import MongoClient


# Basic parameters
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "fluentd"

ORIGIN_COLLECTION = "logs"
ARCHIVE_COLLECTION = "archived_logs"

FAILED_LEVEL = logging.WARNING
ARCHIVE_SIZE = 1 * 1024 * 1024 * 1024  # 1GB

SCRIPT_LOG_LEVEL = logging.INFO

# Prepare logging object.
logging.basicConfig(stream=sys.stderr)
LOG = logging.getLogger()
LOG.setLevel(SCRIPT_LOG_LEVEL)

# Prepare MongoDB client instance.
client = MongoClient(MONGO_HOST, MONGO_PORT)

# Log database object in MongoDB.
db = client[MONGO_DB]

# Create a new log archive database if missing.
if ARCHIVE_COLLECTION not in db.collection_names():
    db.create_collection(ARCHIVE_COLLECTION, size=ARCHIVE_SIZE, capped=True)

# Log arvhice database object in MongoDB.
odb = client[MONGO_DB][ORIGIN_COLLECTION]
adb = client[MONGO_DB][ARCHIVE_COLLECTION]

# Get request information from log db.
requests = odb.aggregate([
    {"$match": {
        "extra.request_id": {"$exists": 1}
    }},
    {"$group": {
        "_id": "$extra.request_id",
        "maxlevelno": {"$max": "$levelno"},
        "starttime": {"$min": "$created"},
        "endtime": {"$max": "$created"},
    }},
])['result']
LOG.info("%d requests" % len(requests))
for request in requests:
    LOG.debug("Request ID: %s" % request["_id"])

# Get non-archived failed logs.
failed_logs = list(
    odb.find({
        "levelno": {"$gte": FAILED_LEVEL},
    }))
LOG.info("%d failed logs" % len(failed_logs))
for failed_log in failed_logs:
    LOG.debug("Failed Log ID: %s" % failed_log["_id"])

# Collect requests when something failed.
related_requests = []
for request in requests:
    for log in failed_logs:
        if request['starttime'] <= log['created'] <= request['endtime']:
            related_requests.append(request['_id'])
            break
LOG.info("%d related requests" % len(related_requests))

# Get logs for related requests.
related_logs = odb.find({
    "extra.request_id": {"$in": related_requests},
    "archived": False,
})
LOG.info("%d related logs to archive" % related_logs.count())

# Save related logs into archive.
for log in related_logs:
    try:
        adb.save(log)
        log['archived'] = True
        odb.save(log)
    except:
        pass

# Save failed logs into archive.
for log in failed_logs:
    try:
        adb.save(log)
        log['archived'] = True
        odb.save(log)
    except:
        pass

LOG.info("done.")
