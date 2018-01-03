from mapscript import mapObj

def application(env, start_response):
    print env["mapfile"]
    start_response('200 OK', [('Content-Type','text/html')])
    return [b"Hello World"]

