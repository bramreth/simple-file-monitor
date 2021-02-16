"""

https://docs.python.org/3/library/http.server.html


here is some example code I looked at to jumpstart setting up the http server.
https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import urllib
import sys
import logging
import os
import pathlib
import hashlib
import json
import shutil

dirname = os.path.dirname(__file__)
filename = dirname


def get_hash(path_in):
    """
    take a pathlib path and return a hash of the given file
    :param path_in:
    :return:
    """
    with open(path_in, 'rb') as payload:
        file_hash = hashlib.md5()
        # boilerplate code, let's us hash larger files
        for chunk in iter(lambda: payload.read(4096), b""):
            file_hash.update(chunk)
        return file_hash.hexdigest()


class FileServer(BaseHTTPRequestHandler):
    valid_suffix = [".txt"]

    def handle_modify(self, data):
        logging.info("handle modify")
        json_dat = json.loads(data)
        path = pathlib.Path(filename + json_dat['filename'])
        path.write_text(json_dat['contents'])
        self._set_response()

    def handle_create_dir(self, created_name):
        logging.info("handle created directory")
        path = pathlib.Path(filename + created_name)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        else:
            logging.warning("folder already exists")
        self._set_response()

    def handle_create_file(self, created_name):
        logging.info("handle created file")
        path = pathlib.Path(filename + created_name)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.touch()
        else:
            logging.warning("file already exists")
        self._set_response()

    def handle_delete(self, deleted_name):
        logging.info("handle deletion")
        path = pathlib.Path(filename + deleted_name)
        if path.exists():
            if path.is_dir():
                # pathlib can't delete folders with contents, so shutil is used
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)
        else:
            logging.warning("deletion target doesn't exist")
        self._set_response()

    def handle_move(self, data):
        logging.info("handle move/ rename")
        json_dat = json.loads(data)
        src_path = pathlib.Path(filename + json_dat["src"])
        dest_path = pathlib.Path(filename + json_dat["dest"])

        shutil.move(src_path, dest_path)
        self._set_response()

    # a dictionary of post paths and their handler methods, this should be handled by a server framework and decorators
    valid_post_urls = {
        "/modify": handle_modify,
        "/create_dir": handle_create_dir,
        "/create_file": handle_create_file,
        "/delete": handle_delete,
        "/move": handle_move
    }

    def handle_modify_request(self, params):
        if isinstance(params["file"], list) and isinstance(params["hash"], list):
            file = params["file"][0]
            md5 = params["hash"][0]
        else:
            logging.error("invalid modify request parameters", params)
            self._set_response(400)
            return

        path = pathlib.Path(filename + file)
        # for the purposes of this project I only accept text files
        if path.suffix not in self.valid_suffix:
            self._set_response(406)
            return

        if path.exists():
            # let's generate our hash of the file and compare them to find out if we need the updated data.
            file_hash = get_hash(path)
            if file_hash != md5:
                self._set_response()
                logging.info("request this files data")
            else:
                self._set_response(406)
                logging.info("file is up to date and can be ignored")

    # a dictionary of get paths and their handler methods, this should be handled by a server framework and decorators
    valid_get_urls = {
        "/modify_request": handle_modify_request
    }

    # reply to the requester with http status codes, default is 200 ok.
    def _set_response(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    #  act on HTTP POST
    def do_POST(self):
        # only accept paths from whitelist
        if self.path not in self.valid_post_urls.keys():
            self._set_response(400)
            return

        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        # lookup the handler method from the POST dictionary and use it on the posted data
        self.valid_post_urls[self.path](self, post_data.decode('utf-8'))
        # boilerplate response
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

    def do_GET(self):
        # the get path have parameters that need to be extracted and stripped before whitelisting
        parse = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parse.query)
        path = parse.path
        # only accept paths from whitelist
        if path not in self.valid_get_urls.keys():
            self._set_response(400)
            return
        # lookup the handler method from the GET dictionary and use it on the parameters
        self.valid_get_urls[path](self, params)


def run(server_class=HTTPServer, handler_class=FileServer, port=8080):
    """
    boilerplate code for instancing an http server with a custom handler
    :param server_class:
    :param handler_class:
    :param port:
    :return:
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


def setup_and_run(fname):
    """
    update global filename from parameter to synchronise argpassing and runnign the script via import
    :param fname:
    :return:
    """
    global filename
    filename = fname
    run()


if __name__ == '__main__':
    # this should be updated to use argparse
    filename_in = os.path.join(dirname, sys.argv[1]) if len(sys.argv) > 1 else dirname
    setup_and_run(filename_in)

