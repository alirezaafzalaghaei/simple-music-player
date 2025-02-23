import os
import sys
import glob
import socket
from urllib.parse import unquote
from sanic import Sanic, response

# Sanic app initialization
app = Sanic("MusicPlayer")

# Ensure the mp3 directory is provided as a command-line argument
if len(sys.argv) != 2:
    print("usage: server.py /path/to/mp3/folder")
    exit(-1)

real_path = sys.argv[1]
fake_path = "/mp3"

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 4444

def get_ip_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        msg = "Open this link in other computers http://{}:{}".format(ip, PORT_NUMBER)
        print(msg)
        return True
    except Exception:
        msg = (
            "Can't find your local IP address.\n"
            "Use 'ipconfig' (Windows) or 'ifconfig' (Linux) to find your IP address.\n"
            "Your local address is something like 192.168.1.105 or 172.16.1.101.\n"
            "After finding it, open this link in your browser:\n"
            "http://ip_address:{}\nwhere ip_address is your local IP address."
        ).format(PORT_NUMBER)
        print(msg)
        return False
    finally:
        s.close()

@app.route('/')
async def index(request):
    # List mp3 files and build a JSON-like string for each file
    files = glob.glob1(real_path, "*.mp3")
    template = '{{"title": "{1}", "file": "{0}"}},'
    result = ""
    for file_name in files:
        result += template.format(f"{fake_path}/{file_name}", file_name)
    # Read index.html and replace placeholder with the list of files
    with open('index.html', 'r', encoding='utf-8') as index_file:
        content = index_file.read().replace('FILES', result)
    return response.html(content)

@app.route('/static/<path:path>')
async def static_files(request, path):
    # Construct file path from /static directory
    file_path = os.path.join(".", "static", path)
    # Determine mime type based on file extension
    if file_path.endswith('.css'):
        mime = 'text/css'
    elif file_path.endswith('.js'):
        mime = 'text/javascript'
    else:
        mime = 'font/woff2'
    return await response.file(file_path, mime_type=mime)

@app.route(fake_path + "/<name>")
async def serve_music(request, name):
    """Serve MP3 files with Range Requests support for seeking."""
    file_name = unquote(name)
    file_path = os.path.join(real_path, file_name)

    if not os.path.exists(file_path):
        return response.text("File not found", status=404)

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("Range")

    if range_header:
        # Extract the byte range from the Range header
        byte_range = range_header.split("=")[-1]
        start, end = byte_range.split("-")
        start = int(start) if start else 0
        end = int(end) if end else file_size - 1

        if start >= file_size:
            return response.text("Requested range not satisfiable", status=416)

        chunk_size = (end - start) + 1

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": "audio/mpeg",
        }

        with open(file_path, "rb") as file:
            file.seek(start)
            data = file.read(chunk_size)

        return response.raw(data, headers=headers, status=206)

    # If no Range header, serve the full file
    headers = {"Accept-Ranges": "bytes"}
    return await response.file(file_path, headers=headers, mime_type="audio/mpeg")


@app.route('/favicon.ico')
async def favicon(request):
    return await response.file('favicon.ico', mime_type='image/vnd.microsoft.icon')

if __name__ == '__main__':
    get_ip_port()
    app.run(host=HOST_NAME, port=PORT_NUMBER)
