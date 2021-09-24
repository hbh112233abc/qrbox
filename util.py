from pdb import Pdb
import pdb
import socket
import json
import struct
from typing import Iterator, Any
from init import *


def serial_notify(message: dict):
    """串口通知

    Args:
        message (dict): 消息数据
    """
    logger.info(f'serial_notify:{message}')
    if not isinstance(message, dict):
        logger.error('message must json string')
        return
    port = message.get('port')
    if not port:
        logger.error('serial port required')
        return

    data = message.get('data')
    if not serials.get(port):
        logger.error(f'serial port:{port} not found')
        return
    serials[port].write(data.encode('utf-8'))


def websocket_send(client: socket, msg: str):
    """向客户端发送消息

    Args:
        client (socket): 客户端连接
        msg (str): 消息内容

    Returns:
        [type]: [description]
    """
    logger.info(f'send ws message:{msg}')
    head = b'\x81'
    if len(msg) < 126:
        head += struct.pack('B', len(msg))
    elif len(msg) <= 0xFFFF:
        head += struct.pack('!BH', 126, len(msg))
    else:
        head += struct.pack('!BQ', 127, len(msg))

    msg_bytes = head + msg.encode('utf-8')
    result = client.send(msg_bytes)
    logger.info(f'send result:{result}')
    return result


def send_serial_list(client: socket):
    """发送串口列表

    Args:
        client (socket): ws客户端
    """
    data = {
        'action': 'serial_list',
        'data': [x for x in serials.keys()],
    }
    websocket_send(client, json.dumps(data))


def websocket_notify(message: str):
    """通知所有websocket客户端

    Args:
        message (str): 消息内容
    """
    logger.info('notify all ws clients')
    for addr, connection in clients.items():
        logger.info(f'=> {addr}')
        websocket_send(connection, message)


def check_port_name(port_name: str, port_char: Any = None) -> bool:
    """检查端口是否需要的

    Args:
        port_name (str): 端口名称
        port_char (mixed, optional): 匹配内容. Defaults to None.

    Returns:
        bool: 是否符合要求
    """
    if not port_char:
        return True

    if isinstance(port_char, str):
        return port_char in port_name
    if isinstance(port_char, list):
        result = False
        for char in port_char:
            if char in port_name:
                return True
        return result
    return True
