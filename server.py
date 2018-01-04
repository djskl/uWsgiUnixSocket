
def application(env, start_response):
    mapfiles = env["mapfile"]
    print mapfiles
    s = b"hello,world"
    start_response('200 OK', [
        ('Content-Type','text/html'),
        ('Content-Length',str(len(s)))
    ])
    return [s]
