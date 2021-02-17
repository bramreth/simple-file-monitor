"""
watchdog and requests docs were a frequent reference.
https://pypi.org/project/watchdog/
https://pypi.org/project/requests/
"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import hash_file_set

import sys
import time
import logging
import requests
import hashlib
import json

path = ""


# inherit the filesystem event handler and add functionality
class CustomWatcher(FileSystemEventHandler):
    # once the server is actually deployed, this would obviously need to be parmeterised
    # however seeing as the file server has no security unless i change library this should be fine.
    url = 'http://127.0.0.1:8080'

    def on_moved(self, event) -> None:
        """
        when wathdog detects a file has moved, post its source and destination path in json to the server for
        recreation
        :param event:
        :return:
        """
        super(CustomWatcher, self).on_moved(event)
        logging.info(event)

        src_file = event.src_path.lstrip(path)
        dest_file = event.dest_path.lstrip(path)
        json_dat = json.dumps({"src": src_file, "dest": dest_file})

        requests.post(self.url + "/move", data=json_dat)

    def on_created(self, event) -> None:
        """
        when watchdog notices a file is created post the filename to the server with seperate addresses for directories and files
        as depending on which the server will use touch or mkdir, and whether or not a file is a folder becomes
        ambiguous when it is just a path
        :param event:
        :return:
        """
        super(CustomWatcher, self).on_created(event)
        logging.info(event)

        file = event.src_path.lstrip(path)

        # the server needs to know if it's a file or directory to decide whether to use mkdir or touch
        if event.is_directory:
            requests.post(self.url + "/create_dir", data=file)
        else:
            requests.post(self.url + "/create_file", data=file)
            # if we have created a file it may have contents we want to upload.
            # so let's propogate a modified event manually
            self.on_modified(event)

    def on_deleted(self, event) -> None:
        """
        when watchdog notices a path is deleted post it to the server. the server can figure out if that path is a
        directory or file as it has a copy
        :param event:
        :return:
        """
        super(CustomWatcher, self).on_deleted(event)
        logging.info(event)
        file = event.src_path.lstrip(path)
        requests.post(self.url + "/delete", data=file)

    def on_modified(self, event) -> None:
        """
        if watchdog detects a file is modified we want to post its contents to the server, but first we need to check
        the server doesn't already have this file, so we can post the filename and a hash for the server to compare.
        depending on the status code it responds with we can upload the file or move on.
        :param event:
        :return:
        """
        super(CustomWatcher, self).on_modified(event)
        logging.info(event)
        if event.is_directory:
            # modified events for directories are meaningless to us
            return
        file = event.src_path.lstrip(path)
        # boilerplate code to generate the hash for our file
        file_hash = hash_file_set.get_hash(event.src_path)
        # modify request returns 200 if the server has a different hash to us, indicating we should then post the file
        response = requests.get(self.url + "/modify_request", params={"file": file, "hash": file_hash})
        if response.status_code == 200:
            # post the media
            # with open(event.src_path, 'r') as payload:
            #     dat = json.dumps({"filename": file, "contents": payload.read()})
            #     requests.post(self.url + "/modify", data=dat)
            with open(event.src_path, 'rb') as payload:
                # dat = json.dumps({"filename": file, "contents": payload.read()})
                requests.post(self.url + "/modif_bin", files={'upload_file': payload})
        else:
            logging.warning("server file copy already up to date.")


# code from the watchdog library docs
def setup_watchdog(path_in: str) -> None:
    """
    update the folder we are monitoring and launch watchdog, with our custom watcher, to post requests on
    specific events
    :param path_in: str
    :return:
    """
    global path
    path = path_in
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = CustomWatcher()
    observer = Observer()
    # this will setup a watcher with our custom event handler perpetually
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        # this feels greedy but was in the docs for the watchdog library.
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    # this should be updated to use argparse
    setup_watchdog(sys.argv[1] if len(sys.argv) > 1 else '.')
