#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'hbh112233abc@163.com'
import os
import sys
import time

from init import *
from util import *
from ws_server import *
from serial_server import *


def main():
    port_char = ['USB', 'PCI']
    if len(sys.argv) > 1:
        port_char = list(sys.argv[1:])
    logger.info(f'find serail port match port description:{port_char}')
    active_serials = 0
    for port in serial_list_ports():
        port_description = port.description
        logger.info(f'serial port:{port_description}')
        if not check_port_name(port_description, port_char):
            continue
        port_name = port.name
        serial_server = SerialServer(port_name)
        serial_server.setDaemon(True)
        serial_server.start()
        active_serials += 1
    if active_serials < 1:
        logger.error('not found match serial port!!!')

    websocket_server = WebsocketServer(5678)
    websocket_server.setDaemon(True)
    websocket_server.start()

    # os.system('start demo.html')
    while True:
        time.sleep(0.1)


if __name__ == '__main__':
    main()
