import itertools
import logging
import os
import sys
import socket
import threading
import traceback

from fluent import sender
import msgpack
from nova.openstack.common.gettextutils import _
from nova.openstack.common import log


try:
    import json
except ImportError:
    import simplejson as json


class FluentFormatter(object):
    def __init__(self):
        # NOTE(jkoelker) we ignore the fmt argument, but its still there
        #                since logging.config.fileConfig passes it.
        #self.datefmt = datefmt
        self.hostname = socket.gethostname()
        self.binaryname = log._get_binary_name()

    def formatException(self, ei, strip_newlines=True):
        lines = traceback.format_exception(*ei)
        if strip_newlines:
            lines = [itertools.ifilter(
                lambda x: x,
                line.rstrip().splitlines()) for line in lines]
            lines = list(itertools.chain(*lines))
        return lines

    def format(self, record):
        message = {'hostname': self.hostname,
                   #'name': record.name,
                   #'module': record.module,
                   'binary': self.binaryname,
                   'message': record.getMessage(),
                   #'msg': record.msg,
                   'levelname': record.levelname,
                   'levelno': record.levelno,
                   'pathname': record.pathname,
                   #'filename': record.filename,
                   'lineno': record.lineno,
                   'funcname': record.funcName,
                   'created': record.created,
                   #'msecs': record.msecs,
                   #'relative_created': record.relativeCreated,
                   #'thread': record.thread,
                   #'thread_name': record.threadName,
                   #'process_name': record.processName,
                   #'process': record.process,
                   'traceback': None,
                   'archived': False}

        if record.args:
            message['message'] = record.msg % record.args

        if hasattr(record, 'extra'):
            message['extra'] = record.extra

        if record.exc_info:
            message['traceback'] = self.formatException(record.exc_info)

        return message


class FluentHandler(logging.Handler):
    '''
    Logging Handler for fluent.
    '''
    def __init__(self, tag, host='localhost', port=24224, timeout=3.0,
                 verbose=False):

        self.tag = tag
        self.sender = sender.FluentSender(tag,
                                          host=host, port=port,
                                          timeout=timeout, verbose=verbose)
        self.fmt = FluentFormatter()
        logging.Handler.__init__(self)

    def emit(self, record):
        if record.levelno < self.level:
            return
        data = self.fmt.format(record)
        self.sender.emit(None, data)

    def _close(self):
        self.sender._close()
