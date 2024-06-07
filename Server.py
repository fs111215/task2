import socket
import struct
import time
import random
import threading

class Server:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.server_ip, self.server_port))
        print(f"Server listening on {self.server_ip}:{self.server_port}")

    def handle_request(self, request_packet, client_addr):
        seq_no, ver, request_time, content = struct.unpack('!Hc8s192s', request_packet)
        request_time = request_time.decode().strip('\x00')
        content = content.decode().strip('\x00')

        if content == 'SYN':
            print(f"SYN received from {client_addr}, establishing connection.")
            response_packet = struct.pack('!Hc8s192s', seq_no, b'\x02', request_time.encode(), b'SYN-ACK')
            self.socket.sendto(response_packet, client_addr)
            return

        if content == 'ACK':
            print(f"ACK received from {client_addr}, connection established.")
            return

        if content == 'FIN':
            print(f"FIN received from {client_addr}, releasing connection.")
            print()
            response_packet = struct.pack('!Hc8s192s', seq_no, b'\x02', request_time.encode(), b'FIN-ACK')
            self.socket.sendto(response_packet, client_addr)
            return
        print(f"Received request from {client_addr}, Sequence no: {seq_no}, Request time: {request_time}")
        # Simulate random packet loss
        if random.random() < 0.3:  # Simulate 30% packet loss rate
            print(f"Packet loss simulated for sequence no: {seq_no}")
            return

        # Simulate processing time
        time.sleep(random.uniform(0.01, 0.05))  # Simulate processing time between 10ms to 50ms

        # Generate response packet with current system time
        server_time = time.strftime("%H:%M:%S", time.localtime())
        response_packet = struct.pack('!Hc8s192s', seq_no, b'\x02', server_time.encode(), b'Response data')
        self.socket.sendto(response_packet, client_addr)
        print(f"Sent response to {client_addr}, Sequence no: {seq_no}")

    def run(self):
        while True:
            request_packet, client_addr = self.socket.recvfrom(2048)
            threading.Thread(target=self.handle_request, args=(request_packet, client_addr)).start()

if __name__ == "__main__":
    server = Server("127.0.0.1", 8879)  # Changed to port 8888
    server.run()
