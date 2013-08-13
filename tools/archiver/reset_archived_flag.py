#!/usr/bin/python
import logging
import sys

from pymongo import MongoClient


# Basic parameters
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "logcas"

FAILED_LEVEL = logging.WARNING

SCRIPT_LOG_LEVEL = logging.INFO

# Prepare logging object.
logging.basicConfig(stream=sys.stderr)
LOG = logging.getLogger()
LOG.setLevel(SCRIPT_LOG_LEVEL)


def main():
    # Prepare MongoDB client instance.
    client = MongoClient(MONGO_HOST, MONGO_PORT)

    # Log database object in MongoDB.
    db = client[MONGO_DB]

    # Get non-archived failed logs.
    logs = db.logs.update(
        {"archived": True},
        {"$set": {"archived": False}},
        multi=True)
    LOG.info("done.")

if __name__ == "__main__":
    main()
