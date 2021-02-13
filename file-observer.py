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

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_DELETED


# inherit the filesystem event handler and add functionality
class CustomWatcher(FileSystemEventHandler):
    url = 'http://127.0.0.1:8080'
    def on_any_event(self, event):
        super().on_any_event(event)
        """Catch-all event handler.

        :param event:
            The event object representing the file system event.
        :type event:
            :class:`FileSystemEvent`
        """
        print(event)
        if event is EVENT_TYPE_DELETED:
            pass
        elif not event.is_directory and event.src_path:
            #with?
            files = {'files': open(event.src_path, 'rb')}
            values = {'upload_file': event.src_path, 'DB': 'photcat', 'OUT': 'csv', 'SHORT': 'short'}
            r = requests.post(self.url, files=files, data=values)
        else:
            # files = {'files': open('file.txt', 'rb')}
            # values = {'upload_file': 'file.txt', 'DB': 'photcat', 'OUT': 'csv', 'SHORT': 'short'}
            # r = requests.post(url, files=files, data=values)
            """
            we have our event let's post specifics via requests when I know what I want to recienve.
            """
            x = requests.post(self.url, data=event.event_type)

def setup_watchdog(path):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    # this watches a file at a sys argument path
    event_handler = CustomWatcher()
    observer = Observer()
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
    setup_watchdog(path)


# we need a watchdog event handler, then we can have it post the update via requests to the server,
# we could post a hash of the action then check if that update has been done before.