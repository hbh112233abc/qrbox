from loguru import logger

logger.add('log/qrbox.log',
           rotation="00:00",
           backtrace=True,
           diagnose=True,
           encoding='utf-8')

global clients
clients = {}

global serials
serials = {}
