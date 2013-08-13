# LogCAS

This is a log collecting and analyzing system for OpenStack
components.  You can use it to analyze logs on failures quickly and
reduce time to determine problems.

LogCAS stands for "Log Collecting and Analyzing System" but it isn't a
good name. So please name it nicely.


## Features

LogCAS has major features below:

* List logs: list logs from OpenStack components by time series.
* Display a log: print details of a log.
* List requests: list logs per request ID.
* Display a request: list logs for a user request by time series.

* Archive logs: copy logs with important logs (level >= WARNING) and
                logs of user requests processing just at the time to
                another collection in same database on MOngoDB.

Each listing feature has capability below:

* Pagination: specify the number of entries per page and display links
              for other pages.
* Time filter: list logs between a period before/after seconds
  specified.
* Host filter: list logs from a host specified.
* Log level filter: list logs with level >= spefified one.
* Theme: select one from color themes.


## Screenshots

See https://github.com/yosshy/logcas/tree/master/screenshots .


## Basic Structure

LogCAS does below:

* Collects logs from OpenStack components via Fluentd or LogCabin.
* Saves them into MongoDB.
* Displays them by a web application using Flask framework.

Fluent and LogCabin can co-exist but we usually use eather one.
Personally, I like LogCabin because it can overwrite timestamp of logs
on a log server (but it has a limitation described below).

* MongoDB: http://www.mongodb.org/
* Fluentd: http://fluentd.org/
* LogCabin: https://github.com/artirix/logcabin
* Flask: http://flask.pocoo.org/
* PyMongo：http://api.mongodb.org/python/current/
* Flask-PyMongo: http://flask-pymongo.readthedocs.org/
* Flask-WTF: http://pythonhosted.org/Flask-WTF/
* Flask-Testing: http://pythonhosted.org/Flask-Testing/


## Installation and Configuration

### LogCAS Web Application Server

LogCAS web application is besically a Flask application, so you have
to install Flask, Flask-WTK and Flask-PyMongo. If you want to run
unittests, you have to install Flask-Testing and blinker too.

```
# sudo pip install Flask
# sudo pip install Flask-PyMongo
# sudo pip install Flask-WTF
```

Currently, LogCAS has no installer. You have to extract its source
codes with tar for *.tar.gz or unzip for *.ZIP, and move it into a
suitable directory.

Directory structure:

```
logcas/
├── logcas/
│   ├── static/  .. Web static contents (CSS)
│   │   ├── dark.css
│   │   └── default.css
│   ├── templates/  .. Web templates
│   │   ├── archived_log_index.html
│   │   ├── archived_log_show.html
│   │   ├── archived_request_index.html
│   │   ├── archived_request_show.html
│   │   ├── layout.html
│   │   ├── log_index.html
│   │   ├── log_show.html
│   │   ├── macro.html
│   │   ├── request_index.html
│   │   └── request_show.html
│   ├── __init__.py  .. Web application source
│   ├── bootstrap.py
│   ├── log_index.py
│   ├── log_show.py
│   ├── request_index.py
│   ├── request_show.py
│   └── template_filters.py
└── runserver.py  .. Web application startup script
```

There are some parameters in bootstrap.py, so set them for your MongoDB.

```
MONGO_DBNAME = 'logcas'
MONGO_HOST = 'localhost'
MONGO_PORT = '27017'
MONGO_USERNAME = 'foo'
MONGO_PASSWORD = 'bar'
```

Run runserver.py after setting them.


```
# python runserver.py
```

### Log Server

Install MongoDB on the log server (you can also use MongoDB on another
server). See below:
http://docs.mongodb.org/manual/tutorial/install-mongodb-on-linux/

With Fluentd, you can use "capped" option for MongoDB plugin. "capped
collection" is a kind of ring buffer and the oldest log in the
collection will be discarded when the collection get full. You don't
have to mind the size of the collection.

Currently, MongoDB output of LogCabin has no option like it. So create
a capped collection by yourself, or MongoDB will create a usual
collection automatically and it will grow up unlimitedly.

How to create a capped collection:

```
# mongo
MongoDB shell version: 2.4.5
connecting to: test
> use logcas
switched to db logcas
> db.createCollection('logs', {size: 742203392, capped: true })
{ "ok" : 1 }
```

The unit of the size is byte. If you use LogCAS archiver, you can
specify it smaller than RAM to reduce disk I/O.

* Using Fluentd

  Install fluentd. See Fluentd documents for details.

* Using LogCabin

  Intall LogCabin.

  ```
  # sudo pip install logcabin
  ```	 

  Copy logcas/tools/logcabin/mongosaver.py into a suitable directory
  and configure it.

  ```
  Mongodb(database='logcas', collection='logs')`
  ```

  See
  http://logcabin.readthedocs.org/en/latest/outputs.html#module-logcabin.outputs.mongodb
  for details. Run logcabin after setting it.

  ```
  # logcabin -c mongosaver.py &
  ```

If you use the archiver, set parameters in
logcas/tools/archiver/archiver.py like the web application and run it
periodly with cron or a shell script.


### OpenStack Nodes

Extract files as same as web application server and install files
under logcas/logger into a suitable directory in Python path.

/usr/local/lib/python2.7/dist-packages/logcas/logger is good for
it. Make sure that __init__.py file is in it.

A directory structure example:
```
/usr/local/lib/python2.7/dist-packages/logcas/
├── __init__.py  .. an empty file
└── logger/
    ├── __init__.py  .. an empty file
    ├── fluent_logger.py  .. Python logging handler for Fluentd
    └── zmq_logger.py  .. Python logging handler for LogCabin
```

Then, copy logcas/logger/etc_nova_logging.conf to
/etc/nova/logging.conf and modify it if you need.

* Using Fluentd

  ```
  [loggers]
  keys = root, fluent

  [handler_fluent]
  class = logcas.logger.fluent_logger.FluentHandler
  # (category, log server, port)
  args = ('app.nova', 'logserver.example.com', 24224)
  ```
  
* Using LogCabin

  ```
  [loggers]
  keys = root, zmq

  [handler_zmq]
  class = logcas.logger.zmq_logger.ZmqHandler
  # (ZeroMQ URL for the log server,)
  # You need "," at the end of ()
  args = ('tcp://localhost:2120',)
  ```
    
So, intall packages and modules they depend on. You need either you
will use.

* For Python logging handler for Fluentd

  it depends on fluent-logger
  (https://github.com/fluent/fluent-logger-python). After installing
  it, nova services may not run because kombu package is old. If so,
  upgrade kombu package up to date.
  
  ```
  # sudo apt-get install python-pip python-dev build-essential
  # sudo pip install fluent-logger
  # sudo pip install -U kombu
  ```
  
* For Python logging handler for LogCabin

  It depends on pyzmq but it requres newer distribute and
  gevent. Install them at once.

  ```
  # sudo apt-get install python-pip python-dev build-essential \
                          libzmq-dev libevent-dev
  # sudo pip install -U distribute
  # sudo pip install gevent
  # sudo pip install pyzmq
  ```
  
Run nova services after the configration. Try to run them on a shell
at first and make sure that they work.

```
# sudo nova-scheduler
```

With LogCabin, nova-api fails to start because of fork()-related bug
of ZeroMQ. So you must use nova-api-os-compute and nova-api-metadata
to avoid it.

After they work, restart nova services with service command:

```
# sudo service nova-scheduler start
```

## Testing

Run mongo command on the log server and check that there are logs on
the collection.

```
# mongo
MongoDB shell version: 2.4.5
connecting to: test
> show dbs
local   0.078125GB
logcas  4.451171875GB
test    0.203125GB
> use logcas
switched to db logcas
> db.logs.find().count()
770
```

## Usage

Open http://WebApServer:5000/ on a web browser.

There are tabs under the title. See:

* Requests: list logs per request IDs.
* Logs: list logs by time series.
* Requests(Archived): list archived logs per request IDs.
* Logs(Archived): list archived logs by time series.

Note: "(Archived)" tabs have no logs before the archiver runs.

### Pagination, Log-level Filter

There are forms for a number of entries per page and lowest log-level.
Set them and push the submit button.

If there are more entries than it, pagination links are displayed to
specify the page number. The pagination can have links for next and
previous 1-9 pages, jumping to 10 page before and after of the current
and the first and the last depending on the current page number.

### List Logs with Same Request ID

Each request ID in a log list is a link and you will see log list with
the request ID by time series if you click it.

### Time Filter

Each time in the log list is a link and you will see logs before/after
a period (10 seconds by default) if you click it. In this case, you
will see a text form to specify the period by second.


### Host Filter

Each hostname in the log list is a link and you will see logs from the
host if you click it.

### Theme Selector

There is a select form at the right-up corner. Select a theme and push
the submit button, and colors will be changed.

## License

Apache License ver.2.0
