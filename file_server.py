"""
https://docs.python.org/3/library/http.server.html
here is some example code I looked at to jumpstart setting up the http server.
https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
"""

from http.server import BaseHTTPRequestHandler, HTTPServer

import hash_file_set

import urllib
import sys
import logging
import os
import pathlib
import json
import shutil
import ipdb

dirname = os.path.dirname(__file__)
filename = dirname


class FileServer(BaseHTTPRequestHandler):
    valid_suffix = [".txt"]
    hash_set = hash_file_set.HashFileSet()

    def handle_modify_bin(self, data) -> None:
        """
        when a modify request is posted, grab the filename and contents from the json data
        and write the contents to that file. A modify request should be run prior to this
        :param data: str
        :return:
        """
        logging.info("handle modify")
        self.wfile.write(data.encode())
        # ipdb.set_trace()
        # json_dat = json.loads(data)
        # path = pathlib.Path(filename + json_dat['filename'])
        # path.write_text(json_dat['contents'])

    def handle_modify(self, data: str) -> None:
        """
        when a modify request is posted, grab the filename and contents from the json data
        and write the contents to that file. A modify request should be run prior to this
        :param data: str
        :return:
        """
        logging.info("handle modify")
        json_dat = json.loads(data)
        path = pathlib.Path(filename + json_dat['filename'])
        path.write_text(json_dat['contents'])


        # we need to add this file to the filehashset
        self.hash_set.add_hash(path)
        self._set_response()

    def handle_create_dir(self, created_name: str) -> None:
        """
        make a directory at the path with the provided name.
        :param created_name: str
        :return:
        """
        logging.info("handle created directory")
        path = pathlib.Path(filename + created_name)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        else:
            logging.warning("folder already exists")
        self._set_response()

    def handle_create_file(self, created_name: str) -> None:
        """
        touch a file at the path with the provided name
        :param created_name: str
        :return:
        """
        logging.info("handle created file")
        path = pathlib.Path(filename + created_name)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.touch()
        else:
            logging.warning("file already exists")
        self._set_response()

    def handle_delete(self, deleted_name: str) -> None:
        """
        use shutil to delete any contents at the given path if its a directory and unlink if its a file.
        :param deleted_name: str
        :return:
        """
        logging.info("handle deletion")
        path = pathlib.Path(filename + deleted_name)
        if path.exists():
            if path.is_dir():
                # pathlib can't delete folders with contents, so shutil is used
                shutil.rmtree(path)
            else:
                self.hash_set.remove_path(path)
                path.unlink(missing_ok=True)
        else:
            logging.warning("deletion target doesn't exist")
        self._set_response()

    def handle_move(self, data: str) -> None:
        """
        unpack the json source and destination path and use shutil to move the contents appropriately
        :param data: str
        :return:
        """
        logging.info("handle move/ rename")
        json_dat = json.loads(data)
        src_path = pathlib.Path(filename + json_dat["src"])
        dest_path = pathlib.Path(filename + json_dat["dest"])

        shutil.move(src_path, dest_path)
        self.hash_set.move_hash(src_path, dest_path)
        self._set_response()

    # a dictionary of post paths and their handler methods, this should be handled by a server framework and decorators
    valid_post_urls = {
        "/modify": handle_modify,
        "/modif_bin": handle_modify_bin,
        "/create_dir": handle_create_dir,
        "/create_file": handle_create_file,
        "/delete": handle_delete,
        "/move": handle_move
    }

    def handle_modify_request(self, params: dict) -> None:
        """
        read in the provided filename and hash, hash our copy of that file and see if there is a difference.
        if so response with a 200 code to indicate we want the file to be uploaded. otherwise respond with a
        406 not-acceptable
        :param params: dict
        :return:
        """

        if not (isinstance(params["file"], list) and isinstance(params["hash"], list)):
            logging.error("invalid modify request parameters", params)
            self._set_response(400)
            return
        file = params["file"][0]
        md5 = params["hash"][0]

        path = pathlib.Path(filename + file)

        # for the purposes of keeping scope small I only accept text files
        if path.suffix not in self.valid_suffix:
            self._set_response(406)
            return

        if path.exists():
            # let's generate our hash of the file and compare them to find out if we need the updated data.
            file_hash = hash_file_set.get_hash(path)
            if file_hash != md5:
                # now we can check the rest of our hashes

                # if the file already exists in filehashset we can just copy it over
                local_copy = self.hash_set.get_hash_path(md5)
                if local_copy:
                    # copy a local file from the hash set
                    path.write_text(local_copy.read_text())
                    self._set_response(406)
                    logging.info("local copy of file already exists, copying")
                    return

                self._set_response()
                logging.info("request this files data")
            else:
                self._set_response(406)
                logging.info("file is up to date and can be ignored")
        else:
            logging.error("file doesn't exist")

    # a dictionary of get paths and their handler methods, this should be handled by a server framework and decorators
    valid_get_urls = {
        "/modify_request": handle_modify_request
    }

    # reply to the requester with http status codes, default is 200 ok.
    def _set_response(self, code=200) -> None:
        """
        set the response status code for the request, defaults to 200 ok.
        :param code: int
        :return:
        """
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    #  act on HTTP POST
    def do_POST(self) -> None:
        """
        this is an http server function that is called when a post is recieved. here we strain our parameters through
        handler methods in the valid_post_urls dictionary
        :return:
        """
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

    def do_GET(self) -> None:
        """
        this is an http server function that is called when a GET is recieved. here we strain our parameters through
        handler methods in the valid_get_urls dictionary and read any parameters using urllib
        :return:
        """
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


def run(server_class=HTTPServer, handler_class=FileServer, port=8080) -> None:
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


if __name__ == '__main__':
    # this should be updated to use argparse
    filename = os.path.join(dirname, sys.argv[1]) if len(sys.argv) > 1 else dirname
    run()
