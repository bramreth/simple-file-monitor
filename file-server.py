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
import ipdb
import os
import pathlib
import json
import hashlib
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'server_dir')


class FileServer(BaseHTTPRequestHandler):

    def handle_modify(self, dat, len):
        file_and_md5 = json.loads(dat)
        self._set_response()
        for file in file_and_md5:
            path = pathlib.Path(filename + file)
            if path.exists():
                # let's generate our own hash
                hash = self.get_hash(path)
                ipdb.set_trace()
                if hash != file_and_md5[file]:
                    self._set_bad_response()
                    print("send a response that we need that file")
                else:
                    self._set_bad_response()
        #         ipdb.set_trace()
        # ipdb.set_trace()
        print("MODIFY")

    def handle_create_dir(self, dat, len):
        print("CREATE DIR")
        created_name = dat.decode("utf-8")
        path = pathlib.Path(filename + created_name)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        else:
            print("folder already exists")
        self._set_response()

    def handle_create_file(self, dat, len):
        print("CREATE FILE")
        created_name = dat.decode("utf-8")
        path = pathlib.Path(filename + created_name)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.touch()
        else:
            print("file already exists ")
        self._set_response()

        # with filepath.open("w", encoding="utf-8") as f:
        #     f.write(result)

    def handle_delete(self, dat, len):
        print("DELETE FILE")
        deleted_name = dat.decode("utf-8")
        path = pathlib.Path(filename + deleted_name)
        if path.exists():
            if path.is_dir():
                # error if path ahs contents, need a recursive appraoch
                path.rmdir()
            else:
                path.unlink(missing_ok=True)
        else:
            print("folder doesn't exist")
        self._set_response()

    def get_hash(self, path_in):
        with open(path_in, 'rb') as payload:
            hash = hashlib.md5()
            for chunk in iter(lambda: payload.read(4096), b""):
                hash.update(chunk)
            return hash.hexdigest()

    def handle_close(self, dat, len):
        self._set_response()
        print("CLOSE")

    def handle_move(self, dat, len):
        self._set_response()
        print("MOVE")

    valid_urls = {
        "/modify": handle_modify,
        "/create_dir": handle_create_dir,
        "/create_file": handle_create_file,
        "/delete": handle_delete,
        "/close": handle_close,
        "/move": handle_move
    }

    def _set_continue_response(self):
        self.send_response(100)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_bad_response(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # listen to posted info
    def do_POST(self):

        """
        self.path can be:
            -modify
            -delete
            -create
            -close
            -move
        :return:
        """
        if self.path not in self.valid_urls.keys():
            self._set_bad_response()
            return

        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        self.valid_urls[self.path](self, post_data, content_length)
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        # ipdb.set_trace()
        # self._set_response()
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

"""
/create is imediately followed by /move
two /modifies in a row

for my own security there will be one updating dir on the server that gets overwritten by the client whenever
it is launched

os.makedirs os.create file?

os.rename
os.mkdir
os.mknod makes a file
"""