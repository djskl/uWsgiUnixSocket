import socket
import struct
from binascii import hexlify

def force_bytes(value):
    if isinstance(value, bytes):
        return value
    return str(value).encode('utf-8')


def encode_uwsgi_vars(values):
    """
    Encode a list of key-value pairs into an uWSGI request header structure.
    """
    # See http://uwsgi-docs.readthedocs.io/en/latest/Protocol.html#the-uwsgi-vars
    buffer = []
    for key, value in values:
        key_enc = force_bytes(key)
        val_enc = force_bytes(value)
        buffer.append(struct.pack('<H', len(key_enc)))
        buffer.append(key_enc)
        buffer.append(struct.pack('<H', len(val_enc)))
        buffer.append(val_enc)
    return b''.join(buffer)


def send_uwsgi_request(socket, header_content):
    data = encode_uwsgi_vars(header_content)
    header = struct.pack(
        '<BHB',
        0,  # modifier1: 0 - WSGI (Python) request
        len(data),  # data size
        0,  # modifier2: 0 - always zero
    )
    socket.sendall(header)
    socket.sendall(data)


def dump_from_socket(socket, width=32):
    while True:
        chunk = socket.recv(width)
        if not chunk:
            break
        print('%-*s  %s' % (
            width * 2,
            hexlify(chunk).decode(),
            ''.join(b if b.isprintable() else '.' for b in chunk.decode('ascii', 'replace'))
        ))


sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

server_address = './mapserver.sock'
print 'connecting to %s' % server_address

sock.connect(server_address)

with open("/mnt/f25/mapserver/temp.map", "r") as reader:
    cnt = reader.read()

send_uwsgi_request(sock, {"PATH_INFO": "/", "mapfile": cnt}.items())

chunk = sock.recv(1024)

print chunk

sock.close()
