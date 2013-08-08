#!/usr/bin/python
import logging
import sys

from pymongo import MongoClient


# Basic parameters
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "fluentd"

ORIGIN_COLLECTION = "logs"

FAILED_LEVEL = logging.WARNING

SCRIPT_LOG_LEVEL = logging.INFO

# Prepare logging object.
logging.basicConfig(stream=sys.stderr)
LOG = logging.getLogger()
LOG.setLevel(SCRIPT_LOG_LEVEL)

# Prepare MongoDB client instance.
client = MongoClient(MONGO_HOST, MONGO_PORT)

# Log database object in MongoDB.
db = client[MONGO_DB]

# Log arvhice database object in MongoDB.
odb = client[MONGO_DB][ORIGIN_COLLECTION]

# Get non-archived failed logs.
logs = odb.find_and_modify(
    query={"archived": True},
    update={"archived": False})
LOG.info("done.")
