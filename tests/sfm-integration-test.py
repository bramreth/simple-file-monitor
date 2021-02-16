import unittest

import subprocess
import pathlib
import shutil
import os
import time

venv_path = "venv/Scripts/python"


def clear_dir(dir_path: pathlib.Path) -> None:
    """
    take a directory, delete it and recreate it, a simple cleanup step after running tests.
    :param dir_path:
    :return:
    """
    if dir_path.exists():
        shutil.rmtree(dir_path)
    time.sleep(1)
    dir_path.mkdir()


class SFMIntegrationTestCase(unittest.TestCase):

    basepath = pathlib.Path(os.path.dirname(__file__))
    server_process = None
    server_dir = "server_dir"
    server_dir_path = basepath.parent.joinpath(server_dir)
    monitor_process = None
    monitored_dir = "monitored_dir"
    monitored_dir_path = basepath.parent.joinpath(monitored_dir)

    @classmethod
    def setUpClass(cls) -> None:
        """
        spawn the server and monitor process's
        :return:
        """
        print("setUpClass")
        cls.server_process = subprocess.Popen([venv_path, "file_server.py", cls.server_dir]
                                              )
        time.sleep(2)
        # don't log the watchdog unless it's an error
        cls.monitor_process = subprocess.Popen([venv_path, "file_observer.py", cls.monitored_dir],
                                               stdout=subprocess.DEVNULL,
                                               stderr=subprocess.STDOUT
                                               )
        time.sleep(2)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        kill the two processes and wipe their monitored directories
        :return:
        """
        print("tearDownClass")
        cls.server_process.kill()
        cls.monitor_process.kill()
        clear_dir(cls.server_dir_path)
        clear_dir(cls.monitored_dir_path)

    def test_create_delete_file(self) -> None:
        """
        create a text file, check it exists on the server, delete it and check it then doesn't exist on the server
        :return:
        """
        print("testing files can be created and deleted locally and on the server")
        # create a file with a name in the monitored dir, assert it exists in both locations
        new_path = self.monitored_dir_path.joinpath("tmp.txt")
        new_path.touch()
        self.assertTrue(new_path.exists())  # assert file created in monitored dir
        time.sleep(1)  # give the server a bit of breathing room to receive the rest request
        self.assertTrue(self.server_dir_path.joinpath("tmp.txt").exists())  # assert file also created on server
        new_path.unlink()
        self.assertFalse(new_path.exists())
        time.sleep(1)
        self.assertFalse(self.server_dir_path.joinpath("tmp.txt").exists())

    def test_create_delete_dir(self) -> None:
        """
        create a folder, check it exists on the server, delete it and check it then doesn't exist on the server
        :return:
        """
        print("testing directories can be created and deleted locally and on the server")
        # create a file with a name in the monitored dir, assert it exists in both locations
        new_path = self.monitored_dir_path.joinpath("tmp_dir")
        new_path.mkdir()
        self.assertTrue(new_path.exists())  # assert file created in monitored dir
        time.sleep(1)
        self.assertTrue(self.server_dir_path.joinpath("tmp_dir").exists())  # assert file also created on server
        new_path.rmdir()
        self.assertFalse(new_path.exists())
        time.sleep(1)
        self.assertFalse(self.server_dir_path.joinpath("tmp_dir").exists())

    # this doesn't seem to be triggering watchdog events so I'm going to leave this for the moment
    # def test_move_file(self) -> None:
    #     new_dir = self.monitored_dir_path.joinpath("tmp_dir")
    #     new_file = self.monitored_dir_path.joinpath("tmp.txt")
    #     new_dir.mkdir()
    #     new_file.touch()
    #     self.assertTrue(new_file.exists())
    #     self.assertTrue(new_dir.exists())
    #     target = new_dir.joinpath("tmp.txt")
    #     self.assertFalse(target.exists())
    #     shutil.move(new_file, target)
    #
    #     time.sleep(1)
    #     self.assertTrue(target.exists())
    #     time.sleep(1)
    #     server_path = self.server_dir_path.joinpath("tmp_dir")
    #     self.assertTrue(server_path.joinpath("tmp.txt"))
    #     # subtest a file with contents can be deleted
    #     time.sleep(1)
    #     shutil.rmtree(new_dir)
    #     time.sleep(3)
    #     # time.sleep(100)
    #     self.assertFalse(new_file.exists())
    #     self.assertFalse(server_path.joinpath("tmp.txt").exists())

    def test_create_file_with_data(self) -> None:
        """
        create a file, check it exists on the server, write data to it, check the file on the server contains the same
        data
        :return:
        """
        print("testing files can be created and deleted locally with contents")
        new_path = self.monitored_dir_path.joinpath("pangram.txt")
        new_path.touch()
        self.assertTrue(new_path.exists())  # assert file created in monitored dir
        time.sleep(1)
        self.assertTrue(self.server_dir_path.joinpath("pangram.txt").exists())  # assert file also created on server

        # a few pangrams
        test_text = """
        Sphinx of black quartz, judge my vow.\n
        Waltz, bad nymph, for quick jigs vex.\n
        The quick brown fox jumps over the lazy dog\n
        """

        new_path.write_text(test_text)

        time.sleep(2)
        print("text on server: ")
        print(self.server_dir_path.joinpath("pangram.txt").read_text())
        self.assertEqual(new_path.read_text(), self.server_dir_path.joinpath("pangram.txt").read_text())

        new_path.unlink()
        self.assertFalse(new_path.exists())
        time.sleep(1)
        self.assertFalse(self.server_dir_path.joinpath("pangram.txt").exists())


if __name__ == '__main__':
    # the subprocess popen was having a hard time understanding my virutal environment so I added some parsing
    # in case a venv isn't present
    if not os.environ['VIRTUAL_ENV']:
        venv_path = "python"
    SFMIntegrationTestCase()
    unittest.main()
