import socket
import struct
import time
import random
import threading

class Server:
    def __init__(self, server_ip, server_port):
        # 初始化服务器对象，绑定IP地址和端口号
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #创建UDP套接字
        self.socket.bind((self.server_ip, self.server_port))
        print(f"Server listening on {self.server_ip}:{self.server_port}")

    def handle_request(self, request_packet, client_addr):
        #处理客户端的请求
        seq_no, ver, request_time, content = struct.unpack('!Hc8s192s', request_packet) #struct.unpack函数对二进制数据包request_packet进行解析
        #Hc8s192s分别表示一个无符号短整型（2个字节），c表示一个字符和8s表示8个字节的字符串，192s表示解析一个192字节的字符串。
        request_time = request_time.decode().strip('\x00') #对解析后的请求时间进行解码并去除末尾的空字符（\x00），得到字符串格式的请求时间。
        content = content.decode().strip('\x00') #得到字符串格式的内容

        if content == 'SYN': #建立连接请求
            print(f"SYN received from {client_addr}, establishing connection.")

            #构造响应数据包
            response_packet = struct.pack('!Hc8s192s', seq_no, b'\x02', request_time.encode(), b'SYN-ACK')
            self.socket.sendto(response_packet, client_addr)
            return

        if content == 'ACK': #连接已建立
            print(f"ACK received from {client_addr}, connection established.")
            return

        if content == 'FIN': #释放连接请求
            print(f"FIN received from {client_addr}, releasing connection.")

            #构造响应数据包
            response_packet = struct.pack('!Hc8s192s', seq_no, b'\x02', request_time.encode(), b'FIN-ACK')
            self.socket.sendto(response_packet, client_addr)
            return

        if content == 'END-ACK': #连接释放完成
            print(f"FIN_END_ACK received from {client_addr}")
            print()
            return

        #打印收到请求的消息：客户端地址、序列号和请求时间
        print(f"Received request from {client_addr}, Sequence no: {seq_no}, Request time: {request_time}")
        # 模拟随机丢包
        if random.random() < 0.3:  # 模拟30%的丢包率
            print(f"Packet loss simulated for sequence no: {seq_no}") #打印丢包序列号
            return

        # 模拟处理时间在10ms到50ms之间
        time.sleep(random.uniform(0.01, 0.05))

        # 生成带有当前系统时间的响应数据包
        server_time = time.strftime("%H:%M:%S", time.localtime())
        response_packet = struct.pack('!Hc8s192s', seq_no, b'\x02', server_time.encode(), b'Response data')
        self.socket.sendto(response_packet, client_addr)
        print(f"Sent response to {client_addr}, Sequence no: {seq_no}")

    def run(self):
        while True:
            request_packet, client_addr = self.socket.recvfrom(2048) #从缓冲区中接收请求数据包和客户端地址
            threading.Thread(target=self.handle_request, args=(request_packet, client_addr)).start() #创建线程使服务器能够同时处理多个客户端的请求

if __name__ == "__main__":
    server = Server("127.0.0.1", 8880)  # Changed to port 8880
    server.run()
