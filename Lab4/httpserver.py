import asyncio
import os
import mimetypes
import urllib


keys=('method','path')


class HTTPHeader:
    def __init__(self):
        self.headers={key:None for key in keys}

    def parse_header(self,line):
        fileds = line.split(' ')
        if fileds[0] == 'GET' or fileds[0] == 'HEAD'or fileds[0]=='POST':
            self.headers['method']=fileds[0]
            self.headers['path']=fileds[1]

    def get(self,key):
        return self.headers.get(key)

async def dispatch(reader,writer):
    content_size = ''
    while True:
        data  = await reader.readline()
        msg=data.decode()
        #print(msg)
        header = HTTPHeader()
        header.parse_header(msg)



        method=header.get('method')
        path = './' + header.get('path')
        if method=='GET':

            if path=='.//':

                writer.writelines([
                    b'HTTP/1.0 200 OK\r\n',
                    b'Content-Type:text/html\r\n',
                    b'Connection: close\r\n',
                    b'\r\n',
                    b'\r\n'])
                await writer.drain()

                list=os.listdir(path)
                writer.writelines([
                b'<html><head><meta charset="UTF-8"><title>Homepage</title></head>\r\n',
                b'  <body bgcolor="white">\r\n',
                b'<h1>Homepage</h1><hr>\r\n',
                b'<pre>\r\n'])
                await writer.drain()
                st=''
                for a in list:
                        #print(a)
                        st+=('<a href="'+a+'">'+a+'</a><br>'+'\r\n')#b'<a href="venv/">venv/</a><br>'
                        #print(st)

                writer.write(st.encode())
                await writer.drain()

                writer.writelines([
                b'</pre>\r\n',
                b'<hr>\r\n',
                b' </body></html>\r\n'])
                await writer.drain()


                break

            elif os.path.isdir(path):
                writer.writelines([
                    b'HTTP/1.0 200 OK\r\n',
                    b'Content-Type:text/html\r\n',
                    b'Connection: close\r\n',
                    b'\r\n',
                    b'\r\n'])
                await writer.drain()


                list=os.listdir(path)
                writer.writelines([
                b'<html><head><title>Homepage</title></head>\r\n',
                b'  <body bgcolor="white">\r\n',
                b'<h1>Homepage</h1><hr>\r\n',
                b'<pre>\r\n'])
                await writer.drain()

                for a in list:

                        st=('<a href="'+a+'">'+a+'</a><br>'+'\r\n').encode(encoding='utf-8')#b'<a href="venv/">venv/</a><br>'
                        print(st)
                        writer.write(st)
                        await writer.drain()


                writer.writelines([
                b'</pre>\r\n',
                b'<hr>\r\n',
                b' </body></html>\r\n'])
                await writer.drain()


                break

            elif os.path.isfile(path):
                type=mimetypes.guess_type(path)[0]
                type=str(type).encode()

                writer.writelines([
                    b'HTTP/1.0 200 OK\r\n',
                    b'Content-Type:',type,b';charset=utf-8',b'\r\n'
                    b'Connection: close\r\n',
                    b'\r\n',
                    b'\r\n'])
                await writer.drain()


                file = open(path, 'rb')
                writer.write(file.read())

                await writer.drain()
                file.close()
                break

            else:
              writer.write(b'404 not found')
              await writer.drain()
              break
        elif method=='HEAD':
            if os.path.isfile(path):
                type = mimetypes.guess_type(path)[0]
                type = str(type).encode()

                writer.writelines([
                    b'HTTP/1.0 200 OK\r\n',
                    b'Content-Type:', type, b'\r\n'
                                            b'Connection: close\r\n',
                    b'\r\n',
                    b'\r\n'])
                await writer.drain()
            else:
                writer.writelines([
                b'HTTP/1.0 200 OK\r\n',
                b'Content-Type:text/html\r\n',
                b'Connection: close\r\n',
                b'\r\n',
                b'\r\n'])
                await writer.drain()
        else:
            writer.writelines([
                b'405 Method Not Allowed\r\n',
                ])
            await writer.drain()



    writer.close()



if __name__=='__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch,'127.0.0.1',8080,loop=loop)
    server = loop.run_until_complete(coro)

    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()



