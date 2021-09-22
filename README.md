# 扫码盒子客户端

## websocket服务
- 端口 `5678`
- `ws://127.0.0.1:5678`连接
- 发送数据格式为JSON格式

### 连上ws服务收到串口列表
```
{
  "action":"serial_list",
  "data":["COM5","COM6"]
}
```

### 扫码后ws通知消息
```
{
  "action":"serial_list",
  "port":"COM6",
  "data":"扫码内容"
}
```

### 语音播报消息
```
{
  "action":"sound",
  "port":"COM6",
  "data":"Test Voice = 00 sig."
}
```

### 打包脚本
```
pyinstaller -F --clean .\qrbox.py --add-data="demo.html;."
```
