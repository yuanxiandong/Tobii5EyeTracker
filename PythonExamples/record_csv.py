import socket
import csv
from datetime import datetime

# ---------- 请不要修改这里的代码！ ----------
# 套接字通信的准备 (AF_INET: IPv4通信, SOCK_DGRAM: UDP通信形态)
sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
# 定义接收通信的IP地址·端口号
sock.bind(('127.0.0.1', 1235))
# ----------------------------------------------------------

# 用于添加CSV行的数组
csv_rows = [['timestamp [micros]', 'x', 'y']]

print('等待消息中')

while True:
    try :
        # 等待客户端发来的消息
        message, client_addr = sock.recvfrom(1024)

        # 收到消息后解码为字符串格式·用逗号分隔
        row = message.decode(encoding='utf-8').split(',')
        # 如果行格式不正确则跳过
        if len(row) != 3:
            continue

        print(datetime.fromtimestamp(int(row[0]) / 1000000), ':', '(', row[1], ',', row[2], ')')

        # 添加到csv rows
        csv_rows.append(row[:3])

    # 按Ctrl+C中止执行时
    except KeyboardInterrupt:
        sock.close()
        break

# 记录当前时刻
now = datetime.now().strftime('%Y%m%d-%H%M%S')
# 保存csv文件
with open(now + '.csv', 'w', newline='') as f:
    csv.writer(f).writerows(csv_rows)

print('写入文件:', now + '.csv')