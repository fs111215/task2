import socket
import struct
import time
import statistics
import sys
VERSION = b'\x02'
SYN = 'SYN'
FIN = 'FIN'
ACK = 'ACK'
SYN_ACK = 'SYN-ACK'
FIN_ACK = 'FIN-ACK'

class Client:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.seq_no = 0
        self.rtt_times = []
        self.start_time = None
        self.end_time = None
        self.sent_packets = 0

    def send_packet(self,  data):
        if data not in [ACK, SYN, SYN_ACK, FIN, FIN_ACK]:
            self.seq_no += 1
        else:
            self.seq_no = 0
        request_time = time.strftime("%H:%M:%S", time.localtime())
        packet = struct.pack('!Hc8s192s', self.seq_no, VERSION, request_time.encode(), data.encode())
        self.socket.sendto(packet, (self.server_ip, self.server_port))

    def send_request(self, data):
        self.send_packet(data)

        for attempt in range(3):  # Try sending up to 3 times
            start_time = time.time()
            self.sent_packets += 1

            try:
                self.socket.settimeout(0.1)  # Set timeout to 100ms
                response_packet, _ = self.socket.recvfrom(2048)
                end_time = time.time()
                rtt = (end_time - start_time) * 1000  # Convert to milliseconds
                self.rtt_times.append(rtt)
                seq_no, ver, server_time, _ = struct.unpack('!Hc8s192s', response_packet)
                server_time = server_time.decode().strip('\x00')
                print(f"Sequence no: {seq_no}, Server IP: {self.server_ip}, Server Port: {self.server_port}, RTT: {rtt:.2f} ms, Server Time: {server_time}")
                break  # Exit the retry loop on successful response
            except socket.timeout:
                print(f"Sequence no: {self.seq_no}, Request timed out (Attempt {attempt + 1})")

        # Capture start and end time for server response time calculation
        if self.start_time is None:
            self.start_time = time.time()
        self.end_time = time.time()

    def run(self):
        # Simulate connection establishment
        print("Establishing connection...")
        self.send_packet(SYN)
        try:
            self.socket.settimeout(1)  # Wait up to 1 second for SYN-ACK
            response_packet, _ = self.socket.recvfrom(2048)
            seq_no, ver, server_time, content = struct.unpack('!Hc8s192s', response_packet)
            content = content.decode().strip('\x00')
            if content == SYN_ACK:
                print("Connection established.")
                self.send_packet(ACK)
            else:
                print("Failed to establish connection.")
                return
        except socket.timeout:
            print("Connection establishment timed out.")
            return

        # Send data requests
        while self.seq_no < 12:
            data = 'A' * 192  # Placeholder data
            self.send_request(data)

        # Simulate connection release
        print("Releasing connection...")
        self.send_packet(FIN)
        try:
            self.socket.settimeout(1)  # Wait up to 1 second for FIN-ACK
            response_packet, _ = self.socket.recvfrom(2048)
            seq_no, ver, server_time, content = struct.unpack('!Hc8s192s', response_packet)
            content = content.decode().strip('\x00')
            if content == FIN_ACK:
                print("Connection released.")
            else:
                print("Failed to release connection.")
        except socket.timeout:
            print("Connection release timed out.")

        self.socket.close()

        # Print summary
        received_packets = len(self.rtt_times)
        lost_packets = self.sent_packets - received_packets
        loss_rate = (lost_packets / self.sent_packets) * 100 if self.sent_packets > 0 else 0
        max_rtt = max(self.rtt_times) if self.rtt_times else 0
        min_rtt = min(self.rtt_times) if self.rtt_times else 0
        avg_rtt = statistics.mean(self.rtt_times) if self.rtt_times else 0
        rtt_stddev = statistics.stdev(self.rtt_times) if len(self.rtt_times) > 1 else 0
        server_response_time = self.end_time - self.start_time if self.start_time is not None else 0

        print("【Summary】")
        print(f"Sent UDP packets: {self.sent_packets}")
        print(f"Received UDP packets: {received_packets}")
        print(f"Packet loss rate: {loss_rate:.2f}%")
        print(f"Max RTT: {max_rtt:.2f} ms")
        print(f"Min RTT: {min_rtt:.2f} ms")
        print(f"Average RTT: {avg_rtt:.2f} ms")
        print(f"RTT standard deviation: {rtt_stddev:.2f} ms")
        print(f"Server response time: {server_response_time:.2f} seconds")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Client.py <server_ip> <server_port>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    client = Client(server_ip, server_port)
    client.run()
