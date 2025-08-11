import socket

# ---------- 请不要修改这里的代码！ ----------
# 套接字通信的准备 (AF_INET: IPv4通信, SOCK_DGRAM: UDP通信形态)
sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
# 定义接收通信的IP地址·端口号
sock.bind(('127.0.0.1', 1235))
# ----------------------------------------------------------

while True:
    try:
        print('等待消息中')
        # 等待客户端发来的消息
        message, client_addr = sock.recvfrom(1024)
        # 收到消息后解码为字符串格式
        message = message.decode(encoding='utf-8')

        print(f'Received message is [{message}]')

    # 按Ctrl+C中止执行时
    except KeyboardInterrupt:
        print ('\n . . .\n')
        sock.close()
        break
