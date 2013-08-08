from inputs.zeromq import Zeromq
from filters.python import Python
from filters.json import Json
from outputs.mongodb import Mongodb

def timestamp(event):
    from datetime import datetime
    event.time = datetime.today()
    print event

Zeromq()
Json()
Python(timestamp)
Mongodb(database='logcabin', collection='logs')
