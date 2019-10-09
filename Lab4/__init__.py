import asyncio
import os,sys
import mimetypes
from urllib import parse
o = parse.urlparse('https://baidu.com/reco%20de.html')
print(o)
print(os.listdir('./'))
print(os.path.isdir('./'))
print(mimetypes.guess_type('./'))
print(os.path.getsize('./'))
print(os.path.dirname('.'))
print(os.chdir(os.path.dirname('./')))
print(os.path.abspath('.'))

import http.server
import socketserver

PORT = 8888

Handler = http.server.CGIHTTPRequestHandler

with socketserver.TCPServer(('127.0.0.1',PORT),Handler) as httpd:
    print('Serving at port',PORT)
    httpd.serve_forever()
