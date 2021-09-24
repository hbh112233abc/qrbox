import threading
import json

import serial
import serial.tools.list_ports

import chardet

from init import *
from util import *


class SerialServer(threading.Thread):
    def __init__(self, port, ptl=9600, timeout=600):
        super().__init__()
        self.port = port
        self.ptl = 9600
        self.timeout = timeout

    def run(self):
        try:
            server = serial.Serial(self.port, self.ptl, timeout=self.timeout)
            logger.info(f'start serial server port:{self.port}')
            serials[self.port] = server
            while True:
                if server.in_waiting:
                    print('bytes length:', server.in_waiting)
                    try:
                        bytes = server.read(server.in_waiting)
                        logger.info(f'receive qrcode bytes:{bytes}')
                        char_info = chardet.detect(bytes)
                        print(char_info)
                        if int(char_info.get('confidence', 0)) > 0.8:
                            char_code = char_info.get('encoding')
                            data = bytes.decode(char_code)
                        else:
                            try:
                                data = bytes.decode('utf-8')
                            except Exception as e:
                                print(e)
                                data = bytes.decode('gbk')

                        logger.info(f'serial [{self.port}] received:{data}')
                        msg = {
                            'action': 'scan_qrcode',
                            'port': self.port,
                            'data': data,
                        }
                        websocket_notify(json.dumps(msg))
                    except Exception as e:
                        logger.exception(e)

        except Exception as e:
            logger.error(e)


def serial_list_ports():
    """获得串口列表

    Returns:
        list: 串口列表
    """
    return serial.tools.list_ports.comports()
