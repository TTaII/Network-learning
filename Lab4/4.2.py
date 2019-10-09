#!/usr/bin/env python3
'''
Created on 2019��10��3��

@author: lct
'''
import os
import mimetypes
import asyncio
import urllib
from html import escape
keys = ('method', 'path')
err405 = b'HTTP/1.0 405 Method Not Allowed\r\nContent-Type:text/html; charset=utf-8\r\nConnection: close\r\n\r\n<html><body>405 Method Not Allowed</body></html>\r\n\r\n'
err404 = b'HTTP/1.0 404 Not Found\r\nContent-Type:text/html; charset=utf-8\r\nConnection: close\r\n\r\n<html><body>404 Not Found</body></html>\r\n\r\n'
class indexhtml:
    def __init__(self,dir):
        self.dir = dir
    def autoestablish(self):#Create index.html file with dir and path
        html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>Index of .//</title></head><body><div><img src="https://www.sustech.edu.cn/wp-content/uploads/guo70_zh.png" width="100%"></div><h1>Index of .//</h1><hr><ul>'
        endhtml = '</ul><hr></body></html>'
        html+='\r\n<li><a href=\"../\">../</a></li>\r\n'
        for i in range(self.dir.__len__()):
            html+='<li><a href=\"'
            html+=self.dir[i]
            html+='/'
            html+='\">'
            html+=self.dir[i]
            html+='</a></li>\r\n'
        html+=endhtml
        return html
class HTTPHeader:
    def __init__(self):
        self.headers = {key: None for key in keys}
        self.version = 'HTTP/1.0 '
        self.ContentType = 'Content-Type:'
        self.charset = '; charset=utf-8'
        self.ContentLength = 'Content-Length:'
        self.WebServer = 'Server:Tai'
    def parse_header(self, line):
        fileds = line.split(' ')
        if fileds[0] == 'GET' or fileds[0] == 'POST' or fileds[0] == 'HEAD':#Get the method and path info from the line
            self.headers['method'] = fileds[0]
            self.headers['path'] = fileds[1]
    def get(self, key):
        return self.headers.get(key)
    def message(self,state,CT,CL):#Return response header
        return self.version+state+'\r\n'+('' if CL=='none' else self.ContentLength+CL+'\r\n')+('' if CT=='none' else self.ContentType+CT+self.charset+'\r\n')+self.WebServer+'\r\n'+'Connection: close\r\n'+'\r\n'
async def dispatch(reader, writer):
    while True: 
        data = await reader.read(1024)
        message = data.decode()#decode the request header
        httpHeader = HTTPHeader()
        httpHeader.parse_header(message)
        dirpath = os.path.abspath('.')
        if httpHeader.get('method')=='GET':
            filepath = httpHeader.get('path')
            if filepath[-1]=='/':
                filepath = filepath[:-1]
            filepath = urllib.parse.unquote(filepath)#Unquote the filepath from url to normal form
            path = dirpath+ filepath
            path = urllib.parse.unquote(path)#Unquote the path from url to normal form
            filepath = '.'+filepath
            if os.path.isdir(path):#Reply the index.html if the path is dir
                ih = indexhtml(os.listdir(path))
                homepage = ih.autoestablish()
                writer.write(httpHeader.message('200 OK','text/html','none').encode(encoding='utf-8'))#Header's information
                writer.write(homepage.encode())
                await writer.drain()
                break
            try:
                file = open(filepath,'rb')#read binary mode
            except FileNotFoundError:
                writer.write(err404)#Return 404 if no such file exists
                await writer.drain()
                break
            CL=os.path.getsize(filepath)#Return the Content-Length of file
            CT=mimetypes.guess_type(filepath)[0]# Use guess API to get the mimetype of file
            if 'Range:' in message:
                start, end = message[message.index('Range:')+6:-1].strip().strip('bytes=').split('-')
                if start == "":
                    start = CL - end
                else:
                    if end == "":
                        end = CL-1
                start = int(start)
                end = int(end)
                writer.writelines([
                    b'HTTP/1.1 206 Partial Content\r\n',
                    bytes('Content-Type: ' + CT + '\r\n', 'utf-8'),
                    b'Accept-Ranges: bytes\r\n',
                    bytes('Content-Range: ' + 'bytes %s-%s/%s\r\n' % (start, end, CL), 'utf-8'),
                    b'\r\n'
                ])
                file.seek(start)
                writer.write(file.read(end-start+1))
                break
            writer.write(httpHeader.message('200 OK',CT,str(CL)).encode(encoding='utf-8'))#Header's information
            writer.write(file.read())# Write the content of file
            await writer.drain()
            file.close()
            break
        elif httpHeader.get('method')=='HEAD':#Only return the Header's information
            path = '.'+httpHeader.get('path')
            path = urllib.parse.unquote(path)
            if os.path.isdir(path):#Reply the header of dir.html if the path is dir
                writer.write(httpHeader.message('200 OK','text/html','none').encode(encoding='utf-8'))#Header's information
                await writer.drain()
                break
            try:
                CL=os.path.getsize(path)#Return the Content-Length of file
            except FileNotFoundError:
                writer.write(err404)
                await writer.drain()
                break
            CT=mimetypes.guess_type(path)[0]# Use guess API to get the mimetype of file
            writer.write(httpHeader.message('200 OK',CT,str(CL)).encode(encoding = 'utf-8'))#Header's information
            await writer.drain()
            break
        else:
            writer.write(err405) #POST method or other method will return 405
            await writer.drain()
            break
    writer.close()
if __name__ == '__main__': 
    loop = asyncio.get_event_loop() 
    coro = asyncio.start_server(dispatch, '127.0.0.1', 8080, loop=loop) 
    server = loop.run_until_complete(coro)
# Serve requests until Ctrl+C is pressed 
    print('Serving on {} and Hit Ctrl + C to end the server'.format(server.sockets[0].getsockname())) 
    try: 
        loop.run_forever() 
    except KeyboardInterrupt: 
        pass
# Close the server 
    server.close() 
    loop.run_until_complete(server.wait_closed()) 
    loop.close()
