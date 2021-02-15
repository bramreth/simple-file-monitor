"""
this is an interesting problem listening to stuff the two real approaches in my eyes.

Either use a chron job or listen to signals when there are updates. This would be
very OS dependant, but not being wasteful is too much benefit to avoid. I'm currently working on
a windows machine with a linux terminal, I believe I should be able to use linux inotify libs
to track file updates, so let's get that working. a simple constructor that listens to a subdir

https://pypi.org/project/watchdog/
for posting to the server
https://pypi.org/project/requests/
watchdog docs
"""

import sys
import time
import logging
import requests
import hashlib
import json

import ipdb

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

path = ""


# inherit the filesystem event handler and add functionality
class CustomWatcher(FileSystemEventHandler):
    url = 'http://127.0.0.1:8080'
    server_dir = "server_dir"

    def on_moved(self, event):
        super(CustomWatcher, self).on_moved(event)
        print(event)
        src_file = event.src_path.lstrip(path)
        dest_file = event.dest_path.lstrip(path)
        json_dat = json.dumps({"src": src_file, "dest": dest_file})
        x = requests.post(self.url + "/move", data=json_dat)
        # this may not need to post the file just where its moving around

    def on_created(self, event):
        super(CustomWatcher, self).on_created(event)
        print(event)
        # ipdb.set_trace()
        file = event.src_path.lstrip(path)
        if event.is_directory:
            x = requests.post(self.url + "/create_dir", data=file)
        else:
            x = requests.post(self.url + "/create_file", data=file)
            self.on_modified(event)
        #this will need to post  the file

    def on_deleted(self, event):
        super(CustomWatcher, self).on_deleted(event)
        print(event)
        file = event.src_path.lstrip(path)
        # ipdb.set_trace()
        x = requests.post(self.url + "/delete", data=file)
        # this won't need to post any data

    def on_modified(self, event):
        super(CustomWatcher, self).on_modified(event)
        if event.is_directory:
            return
        print(event)
        file = event.src_path.lstrip(path)
        result = 0
        with open(event.src_path, 'rb') as payload:
            hash = hashlib.md5()
            for chunk in iter(lambda: payload.read(4096), b""):
                hash.update(chunk)
            hash = hash.hexdigest()
            print(hash)
            response = requests.get(self.url + "/modify_request", params={"file": file, "hash": hash})
            result = response.status_code
        if result == 200:
            # post the media
            with open(event.src_path, 'r') as payload:
                dat = json.dumps({"filename": file, "contents": payload.read()})
                r = requests.post(self.url + "/modify", data=dat)
        else:
            print("file already present")

    def on_closed(self, event):
        super(CustomWatcher, self).on_closed(event)
        print(event)
        x = requests.post(self.url+ "/close", data=event.event_type)
        # this is likely unimportant


def setup_watchdog():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    # this watches a file at a sys argument path
    event_handler = CustomWatcher()
    observer = Observer()
    # this will setup a watcher with our custom event handler perpetually
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        # this feels greedy
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    setup_watchdog()


# we need a watchdog event handler, then we can have it post the update via requests to the server,
# we could post a hash of the action then check if that update has been done before.


"""
security not in brief
recovering from weird states not in the brief
"""