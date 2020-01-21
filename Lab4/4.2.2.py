# encoding:utf-8
"""
Created on 2019年10月3日

@author: lct
"""
import os
import mimetypes
import asyncio
import urllib

keys = ('method', 'path', 'Range', 'Cookie')
err405 = b'HTTP/1.0 405 Method Not Allowed\r\nContent-Type:text/html; charset=utf-8\r\nConnection: close\r\n\r\n<html><body>405 Method Not Allowed</body></html>\r\n\r\n'
err404 = b'HTTP/1.0 404 Not Found\r\nContent-Type:text/html; charset=utf-8\r\nConnection: close\r\n\r\n<html><body>404 Not Found</body></html>\r\n\r\n'


class IndexHtml:
    def __init__(self, dir):
        self.dir = dir

    def auto_establish(self, directory):  # Create index.html file with dir and path
        html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>Index of ' + directory + '</title></head><body><div><img src="https://www.sustech.edu.cn/wp-content/uploads/guo70_zh.png" width="100%"></div><h1>Index of ' + directory + '</h1><hr><ul>'
        end_html = '</ul><hr></body></html>'
        html += '\r\n<li><a href=\"' + '../' + '\">../</a></li>\r\n'
        for i in range(self.dir.__len__()):
            html += '<li><a href=\"'
            html += self.dir[i]
            html += '/'
            html += '\">'
            html += self.dir[i]
            html += '</a></li>\r\n'
        html += end_html
        return html


def get_cookie(lines):
    dic = {}
    lines = lines.split(';')
    for line in lines:
        key, value = line.strip().split('=', 1)
        if dic.get(key) is None:
            dic[key] = value
    return dic


def get_range(line):
    start, end = line.split('-')
    return start, end


class HTTPHeader:
    def __init__(self):
        self.headers = {key: None for key in keys}
        self.version = '1.0 '
        self.server = 'Tai'
        self.cookie = None
        self.contentLength = None
        self.contentRange = None
        self.contentType = None
        self.last = None
        self.location = None
        self.range = None
        self.state = None

    def parse_header(self, line):
        fileds = line.split(' ')
        if fileds[0] == 'GET' or fileds[0] == 'POST' or fileds[0] == 'HEAD':  # Get the method and path info from the line
            self.headers['method'] = fileds[0]
            self.headers['path'] = fileds[1]
        fileds = line.split(':', 1)
        if fileds[0] == 'Range':
            self.headers['Range'] = get_range(fileds[1].strip().strip('bytes='))
        if fileds[0] == 'Cookie':
            self.headers['Cookie'] = get_cookie(fileds[1])

    def set_version(self, version):
        self.version = version

    def set_location(self, location):
        self.location = location

    def set_state(self, state):
        self.state = state

    def set_info(self, CT, CL):
        self.contentRange = CL
        self.contentType = CT

    def set_range(self):
        start, end = self.headers['Range']
        CL = int(self.contentRange)
        if start == '':
            end = int(end)
            start = CL - end
            end = CL - 1
        if end == '':
            end = CL - 1
        start = int(start)
        end = int(end)
        self.contentLength = str(end - start + 1)
        self.range = (start, end)

    def set_last(self, last):
        self.last = last

    def set_cookie(self):
        self.cookie = ' last=' + self.last + '; Path=/' + '; Max-age=10'

    def get(self, key):
        return self.headers.get(key)

    def message(self):  # Return response header
        return 'HTTP/' + self.version + self.state + '\r\n' \
               + ('Content-Length:' + self.contentLength + '\r\n' if self.contentLength else '') \
               + ('Content-Type:' + self.contentType + '; charset=utf-8' + '\r\n' if self.contentType else '') \
               + 'Server:' + self.server + '\r\n' \
               + ('Set-Cookie:' + self.cookie + '\r\n' if self.cookie else '') \
               + ('Accept-Ranges: bytes\r\n' if self.range else '') \
               + ('Content-Range: bytes ' + str(self.range[0]) + '-' + str(
            self.range[1]) + '/' + self.contentRange + '\r\n' if self.range else '') \
               + ('Location: ' + self.location + '\r\n' if self.location else '') \
               + 'Connection: close\r\n' + '\r\n'


async def dispatch(reader, writer):
    httpHeader = HTTPHeader()
    while True:
        data = await reader.readline()
        message = data.decode()  # decode the request header
        httpHeader.parse_header(message)
        if data == b'\r\n' or data == b'':
            break
    dir_path = os.path.abspath('.')
    if httpHeader.get('method') == 'GET':
        httpHeader.set_state('200 OK')
        file_path = httpHeader.get('path')
        if file_path[-1] == '/' and file_path.__len__() > 1:
            file_path = file_path[:-1]
        file_path = urllib.parse.unquote(file_path)  # Unquote the filepath from url to normal form
        path = dir_path + file_path
        path = urllib.parse.unquote(path)  # Unquote the path from url to normal form
        file_path = '.' + file_path
        if os.path.isdir(path):  # Reply the index.html if the path is dir
            httpHeader.set_last(file_path[1:])
            cookie = httpHeader.get('Cookie')
            httpHeader.set_cookie()
            if file_path == './' and cookie and cookie.get('last') and cookie.get('last') != '/':
                httpHeader.set_location(cookie.get('last') + '/')
                httpHeader.set_state('302 Found')
                filepath = cookie.get('last')
            httpHeader.set_info('text/html', 'none')
            IH = IndexHtml(os.listdir(path))
            homepage = IH.auto_establish(file_path[1:])
            writer.write(httpHeader.message().encode(encoding='utf-8'))  # Header's information
            writer.write(homepage.encode())
        else:
            try:
                file = open(file_path, 'rb')  # read binary mode
                CL = os.path.getsize(file_path)  # Return the Content-Length of file
                CT = mimetypes.guess_type(file_path)[0]  # Use guess API to get the mimetype of file
                httpHeader.set_info(CT, str(CL))
                if httpHeader.get('Range'):
                    httpHeader.set_version('1.1 ')
                    httpHeader.set_state('206 Partial Content')
                    httpHeader.set_range()
                    start, end = httpHeader.range
                    file.seek(start)
                    writer.write(httpHeader.message().encode(encoding='utf-8'))  # Header's information
                    writer.write(file.read(end - start + 1))
                else:
                    writer.write(httpHeader.message().encode(encoding='utf-8'))  # Header's information
                    writer.write(file.read())
            except FileNotFoundError:
                writer.write(err404)  # Return 404 if no such file exists
    elif httpHeader.get('method') == 'HEAD':  # Only return the Header's information
        httpHeader.set_state('200 OK')
        path = '.' + httpHeader.get('path')
        path = urllib.parse.unquote(path)
        if os.path.isdir(path):  # Reply the header of dir.html if the path is dir
            httpHeader.set_info('text/html', 'none')
            writer.write(httpHeader.message().encode(encoding='utf-8'))  # Header's information
        else:
            try:
                CL = os.path.getsize(path)  # Return the Content-Length of file
                CT = mimetypes.guess_type(path)[0]  # Use guess API to get the mimetype of file
                httpHeader.set_info(CT, str(CL))
                writer.write(httpHeader.message().encode(encoding='utf-8'))  # Header's information
            except FileNotFoundError:
                writer.write(err404)
    else:
        writer.write(err405)  # POST method or other method will return 405
    try:
        await writer.drain()
    except BrokenPipeError:
        pass
    writer.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    co_ro = asyncio.start_server(dispatch, '127.0.0.1', 8080, loop=loop)
    server = loop.run_until_complete(co_ro)
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
