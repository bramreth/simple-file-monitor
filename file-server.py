"""
there are an awful lot of options here
curl data across
ssh /scp files across via paramiko

an easy part could be keeping a history of events to decide what to do


requests.post can send a file.

https://docs.python.org/3/library/http.server.html

not for production only basic security checks

https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7

this is stolen but listens to posts at 127.0.0.1:8080/yo
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging


class FileServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # listen to posted info
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=FileServer, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()