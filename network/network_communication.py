import struct


def receive_message(sock):
    data, address = sock.recvfrom(4)
    message_size = int(struct.unpack("!i", data)[0])
    data, address = sock.recvfrom(message_size)
    return data.decode(), address


def send_message(message, address, sock):
    message_size = len(message.encode())
    sock.sendto(struct.pack("!i", message_size), address)
    sock.sendto(message.encode(), address)
