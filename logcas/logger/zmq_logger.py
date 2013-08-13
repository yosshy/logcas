import itertools
import logging
import os
import sys
import socket
import threading
import traceback

from nova.openstack.common.gettextutils import _
from nova.openstack.common import jsonutils
from nova.openstack.common import log
import zmq.green as zmq


class JsonFormatter(object):
    def __init__(self):
        # NOTE(jkoelker) we ignore the fmt argument, but its still there
        #                since logging.config.fileConfig passes it.
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

        return jsonutils.dumps(message)


class ZmqHandler(logging.Handler):
    """Outputs on a zeromq socket.

    :param string address: zeromq address (default: `tcp://*:2120`)
    :param string mode: connect or bind (default: connect)
    :param string socket: PUSH or PUB (default: PUSH)
    """
    def __init__(self, address='tcp://*:2120', mode='connect', socket='PUSH'):
        if mode not in ('connect', 'bind'):
            raise ValueError('mode should be connect or bind')
        if socket not in ('PUSH', 'PUB'):
            raise ValueError('socket should be PUSH or PUB')

        logging.Handler.__init__(self)
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(getattr(zmq, socket))
        self.fmt = JsonFormatter()
        self.address = address
        if mode == 'connect':
            self.sock.connect(self.address)
        else:
            self.sock.bind(self.address)

    def emit(self, record):
        data = self.fmt.format(record)
        self.sock.send(data)

    def _close(self):
        self.sock.close()
