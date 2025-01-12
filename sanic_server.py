import os
import sys
import glob
import socket
from sanic import Sanic
from sanic.response import html

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


app = Sanic(configure_logging=False)
app.static('/static', './static')
app.static('/favicon.ico', './favicon.ico')


@app.route("/")
async def main(request):
    files = glob.glob1(real_path, "*.mp3")
    template = '{{"title": "{1}", "file": "{0}"}},'
    result = ""
    for file_name in files:
        result += template.format("%s/%s" % (fake_path, file_name), file_name)
    with open('index.html') as index:
        return html(index.read().replace('FILES', result))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: server.py /path/to/mp3/folder')
        exit(-1)

    real_path = sys.argv[1]
    fake_path = '/mp3'

    app.static(fake_path, real_path)
    print('Listening to http://%s:%s' % (HOST_NAME, PORT_NUMBER))
    if not get_ip_port():
        exit(-1)
    app.run(host=HOST_NAME, port=PORT_NUMBER, access_log=False, debug=False)
    print('\nShutting down server...')
