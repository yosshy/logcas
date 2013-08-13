import logging
import time

from logcas.bootstrap import *


@app.template_filter('localtime')
def _localtime_filter(dtime):
    return dtime.replace(microsecond=0, tzinfo=None)


@app.template_filter('unixtime')
def _unixtime_filter(dtime):
    return int(time.mktime(dtime.timetuple()))
