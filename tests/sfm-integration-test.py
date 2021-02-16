import unittest

import subprocess
import pathlib
import shutil
import os
import time


def clear_dir(dir_path):
    if dir_path.exists():
        shutil.rmtree(dir_path)
    time.sleep(1)
    dir_path.mkdir()


class MyTestCase(unittest.TestCase):

    basepath = pathlib.Path(os.path.dirname(__file__))
    server_process = None
    server_dir = "server_dir"
    server_dir_path = basepath.parent.joinpath(server_dir)
    monitor_process = None
    monitored_dir = "monitored_dir"
    monitored_dir_path = basepath.parent.joinpath(monitored_dir)

    @classmethod
    def setUpClass(cls):
        print("setUpClass")
        cls.server_process = subprocess.Popen(["venv/Scripts/python", "file_server.py", cls.server_dir])
        time.sleep(3)
        cls.monitor_process = subprocess.Popen(["venv/Scripts/python", "file_observer.py", cls.monitored_dir])
        time.sleep(5)

    @classmethod
    def setUp(cls) -> None:
        print("SETUP")

    @classmethod
    def tearDownClass(cls):
        print("tearDownClass")
        cls.server_process.kill()
        cls.monitor_process.kill()
        clear_dir(cls.server_dir_path)
        clear_dir(cls.monitored_dir_path)

    def test_create_post(self):
        print(self.monitored_dir_path)
        print(self.server_dir_path)
        # create a file with a name in the monitored dir, assert it exists in both locations
        new_path = self.monitored_dir_path.joinpath("tmp.txt")
        new_path.touch()
        time.sleep(1)
        print(new_path.exists())
        print(self.server_dir_path.joinpath("tmp.txt").exists())
        # self.assertEqual(True, False)


if __name__ == '__main__':
    print("start")
    MyTestCase()
    unittest.main()
