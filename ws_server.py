#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'hbh112233abc@163.com'

import socket
import hashlib
import base64
import threading
import json

from init import *
from util import *
from serial_server import serial_notify


class WebsocketServer(threading.Thread):
    """websocket服务

    Args:
        threading (threading): 继承线程对象
    """

    def __init__(self, port=5678):
        super().__init__()
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.port))
        sock.listen(5)
        while True:
            connection, address = sock.accept()
            logger.info(f'accept new client:{address}')
            try:
                username = "ID" + str(address[1])
                thread = WebsocketHandler(connection, username)
                thread.setDaemon(True)
                thread.start()
                clients[username] = connection
            except socket.timeout:
                logger.error('websocket connection timeout!')


class WebsocketHandler(threading.Thread):
    def __init__(self, connection, username):
        super().__init__()
        self.connection = connection
        self.username = username

    def run(self):
        logger.info(f'new websocket client [{self.username}] joined!')
        self.hand_shake()
        send_serial_list(self.connection)
        while True:
            try:
                data = self.connection.recv(1024)
            except socket.error as e:
                logger.error("unexpected error: ", e)
                clients.pop(self.username)
                break
            data = self.parse_data(data)
            if not data:
                continue
            try:
                data = json.loads(data)
                data['user'] = self.username
                logger.info(data)
                if data.get('action', 'sound'):
                    serial_notify(data)
            except Exception as e:
                logger.error('receive data not json')

    def hand_shake(self):
        """客户端连接握手响应

        Returns:
            [type]: [description]
        """
        data = self.connection.recv(1024)
        headers = self.parse_headers(data)
        token = self.generate_token(headers['Sec-WebSocket-Key'])
        msg_list = [
            "HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n",
            "Upgrade: WebSocket\r\n",
            "Connection: Upgrade\r\n",
            f"Sec-WebSocket-Accept: {token}\r\n\r\n",
        ]
        message = ''.join(msg_list)
        return websocket_send(self.connection, message)

    def parse_data(self, info):
        """解析接收的数据

        Args:
            info (bytes): 接收到数据

        Returns:
            str: 解析后的结果
        """
        if not info:
            return ''
        payload_len = info[1] & 127
        if payload_len == 126:
            extend_payload_len = info[2:4]
            mask = info[4:8]
            decoded = info[8:]
        elif payload_len == 127:
            extend_payload_len = info[2:10]
            mask = info[10:14]
            decoded = info[14:]
        else:
            extend_payload_len = None
            mask = info[2:6]
            decoded = info[6:]
        bytes_list = bytearray()  # 使用字节将数据全部收集，再去字符串编码，这样不会导致中文乱码
        for i in range(len(decoded)):
            chunk = decoded[i] ^ mask[i % 4]  # 解码方式
            bytes_list.append(chunk)

        print(bytes_list)
        body = str(bytes_list, encoding='utf-8')
        return body

    def parse_headers(self, msg):
        """解析头部信息

        Args:
            msg (bytes): 接收到的数据

        Returns:
            dict: 解析后的数据
        """
        msg = msg.decode('utf-8')
        logger.info(f'parse header: {msg}')
        headers = {}
        header, data = msg.split('\r\n\r\n', 1)
        for line in header.split('\r\n')[1:]:
            key, value = line.split(': ', 1)
            headers[key] = value
        headers['data'] = data
        return headers

    def generate_token(self, msg):
        """生产token

        Args:
            msg (str): 消息

        Returns:
            str: token
        """
        key = msg + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        ser_key = hashlib.sha1(key.encode('utf-8')).digest()
        return base64.b64encode(ser_key).decode('utf-8')
