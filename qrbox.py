#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'hbh112233abc@163.com'
import os
import time

from init import *
from util import *
from ws_server import *
from serial_server import *


def main():
    for port in serial_list_ports():
        port_description = port.description
        logger.info(f'serial port:{port_description}')
        if 'USB' not in port_description:
            continue
        port_name = port.name
        serial_server = SerialServer(port_name)
        serial_server.setDaemon(True)
        serial_server.start()

    websocket_server = WebsocketServer(5678)
    websocket_server.setDaemon(True)
    websocket_server.start()

    # os.system('start demo.html')
    while True:
        time.sleep(0.1)


if __name__ == '__main__':
    main()
