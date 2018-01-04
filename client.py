import tornado.ioloop
import tornado.iostream
import socket
import struct

def force_bytes(value):
    if isinstance(value, bytes):
        return value
    return str(value).encode('utf-8')

def encode_uwsgi_vars(values):
    buffer = []
    for key, value in values:
        key_enc = force_bytes(key)
        val_enc = force_bytes(value)
        buffer.append(struct.pack('<H', len(key_enc)))
        buffer.append(key_enc)
        buffer.append(struct.pack('<H', len(val_enc)))
        buffer.append(val_enc)
    return b''.join(buffer)

def send_request():
    data = encode_uwsgi_vars({"mapfile":"hello,world"}.items())
    header = struct.pack(
        '<BHB',
        0,  # modifier1: 0 - WSGI (Python) request
        len(data),  # data size
        0,  # modifier2: 0 - always zero
    )
    stream.write(header)
    stream.write(data)
    stream.read_until(b"\r\n\r\n", on_headers)

def on_headers(data):
    print "HEADER:", data
    headers = {}
    for line in data.split(b"\r\n"):
       parts = line.split(b":")
       if len(parts) == 2:
           headers[parts[0].strip()] = parts[1].strip()
    stream.read_bytes(int(headers[b"Content-Length"]), on_body)

def on_body(data):
    print "BODY:", data
    stream.close()
    tornado.ioloop.IOLoop.current().stop()


if __name__ == '__main__':
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    stream = tornado.iostream.IOStream(s)
    stream.connect('./mapserver.sock', send_request)
    tornado.ioloop.IOLoop.current().start()
