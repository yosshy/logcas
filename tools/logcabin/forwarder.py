from inputs.zeromq import Zeromq as ZeromqIn
from outputs.zeromq import Zeromq as ZeromqOut

#LOGSERVER='tcp://LOGSERVER:2120'

ZeromqIn()
ZeromqOut(address=LOGSERVER)
