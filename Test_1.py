import socket
import struct
import time

class Ping:
    def __init__(self, host, count=4, timeout=2):
        self.host = host
        self.count = count
        self.timeout = timeout

    def calculate_checksum(self, packet):
        # Calculate the checksum of the packet
        if len(packet) % 2 != 0:
            packet += b'\x00'  # Pad to even length if necessary

        words = struct.unpack('!{}H'.format(len(packet) // 2), packet)
        checksum = sum(words)

        carry = (checksum >> 16) + (checksum & 0xFFFF)
        checksum = carry + (carry >> 16)

        return ~checksum & 0xFFFF
    def create_packet(self, sequence_number):
        # Create an ICMP Echo Request packet
        icmp_type = 8  # ICMP Echo Request
        icmp_code = 0
        icmp_checksum = 0
        icmp_identifier = 1  # Use a unique identifier
        icmp_data = b"pingpong"

        header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_identifier, sequence_number)
        checksum = self.calculate_checksum(header + icmp_data)
        header = struct.pack("!BBHHH", icmp_type, icmp_code, checksum, icmp_identifier, sequence_number)

        return header + icmp_data

    def send_ping(self, sequence_number):
        # Create a raw socket
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.settimeout(self.timeout)

            packet = self.create_packet(sequence_number)
            sock.sendto(packet, (self.host, 1))  # Use any non-reserved port

            try:
                start_time = time.time()
                data, addr = sock.recvfrom(1024)
                end_time = time.time()

                delay = (end_time - start_time) * 1000  # Convert to milliseconds
                print(f"Reply from {addr[0]}: time={delay:.2f}ms")

            except socket.timeout:
                print("Request timed out.")

    def run(self):
        print(f"Pinging {self.host} with {self.count} packets:")
        for i in range(self.count):
            self.send_ping(i + 1)
            time.sleep(1)  # Pause between each ping

target_host = "lancaster.ac.uk"
ping_tool = Ping(target_host, count=4, timeout=2)
ping_tool.run()
