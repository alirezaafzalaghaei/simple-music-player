import time
import os
import sys
import glob
import socket
from urllib.parse import unquote
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler


HOST_NAME = '0.0.0.0'
PORT_NUMBER = 4444


def get_ip_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = "Open this link in other computers http://%s:%s" % (s.getsockname()[0], PORT_NUMBER)
        print(IP)
        return True
    except:
        IP = """Can't find your local IP address.\nUse 'ipconfig' and 'ifconfig' commands in windows and linux, respectively.\nYour local address is something like 192.168.1.105 or 172.16.1.101.\nAfter finding IP open this link in browser:\nhttp://ip_address:%s\nwhere ip_address is your local IP address.""" % PORT_NUMBER
        print(IP)
        return False
    finally:
        s.close()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class Server(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.handle_index()
        elif self.path.startswith('/static'):
            self.handle_static()
        elif self.path.startswith(fake_path):
            name = self.path[self.path.rindex('/')+1:]
            self.handle_music(unquote(name))
        elif self.path == '/favicon.ico':
            self.handle_favicon()

    def handle_favicon(self):
        file_path = 'favicon.ico'
        self.send_response(200)
        self.send_header('Content-type', 'image/vnd.microsoft.icon')
        self.send_header('Content-length', str(os.path.getsize(file_path)))
        self.end_headers()

        with open(file_path, 'rb', buffering=0) as file:
            self.wfile.write(file.read())

    def handle_music(self, file_name):
        file_path = "%s/%s" % (real_path, file_name)
        self.send_response(200)
        self.send_header('Content-type', 'audio/mpeg')
        self.send_header('Content-length', str(os.path.getsize(file_path)))
        self.end_headers()

        with open(file_path, 'rb', buffering=-1) as file:
            self.wfile.write(file.read())

    def handle_static(self):
        file_path = "./"+self.path
        self.send_response(200)
        if self.path.endswith('css'):
            self.send_header('Content-type', 'text/css')
        elif self.path.endswith('js'):
            self.send_header('Content-type', 'text/javascript')
        else:
            self.send_header('Content-type', 'font/woff2')
        self.send_header('Content-length', str(os.path.getsize(file_path)))

        self.end_headers()

        with open(file_path, 'rb') as file:
            self.wfile.write(bytes(file.read()))

    def handle_index(self):
        files = glob.glob1(real_path, "*.mp3")
        template = '{{"title": "{1}", "file": "{0}"}},'
        result = ""
        for file_name in files:
            result += template.format("%s/%s" % (fake_path, file_name), file_name)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open('index.html') as index:
            content = index.read().replace('FILES', result)
            self.wfile.write(bytes(content, 'UTF-8'))

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: server.py /path/to/mp3/folder')
        exit(-1)

    real_path = sys.argv[1]
    fake_path = '/mp3'

    httpd = ThreadedHTTPServer((HOST_NAME, PORT_NUMBER), Server)
    try:
        print('Listening to http://%s:%s' % (HOST_NAME, PORT_NUMBER))
        if not get_ip_port():
            exit(-1)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
    finally:
        httpd.server_close()
