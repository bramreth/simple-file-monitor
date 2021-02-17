# simple-file-monitor
barebones python file management system

## specification

Build an application to synchronise a source folder and a destination folder over IP:

- 1.1 a simple command line client which takes one directory as argument and keeps
monitoring changes in that directory and uploads any change to its server

- 1.2 a simple server which takes one empty directory as argument and receives any change
from its client

### here we show 1.1 and 1.2 in action
![action view](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/in_action.gif)
![parameter view](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/dir_view.gif)

- Bonus 1. optimise data transfer by avoiding uploading the same file multiple times

### here we have bonus 1 with file hashing to check if data is already present on the server
![reduce uplaod_hash](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/hash_comparison.jpg)

since then I added a more advance hashing system, where the server keeps a class that monitors all the hashes present as well as all the paths taht point to them, so whenever a file is uploaded we can quickly check whether that file exists on the server anywhere already, and we can copy it across instead of uploading the file again.

- Bonus 2. optimise data transfer by avoiding uploading the same partial files (files sharing
partially the same content) multiple times

## instructions
for ease of my development, this project was created on Windows with Pycharm community. As such you would have the easiest recreating this system under those conditions.
- git clone this project and open it in pycharm
- you will be prompted to create a venv from the project requirements, do this using a python interpreter preferably 3.7+ for typing. 

![venv](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/venv.png)

- go to file_server.py and edit the run configuration once the file has finished indexing. 

![config](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/run_config.png)

- choose your python interpreter if it doesn't auto fill and add a prameter with the name of the folder you want the server to monitor  

![server_dir](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/server_dir_config.png)

- repeat this step for file_observer.py, with the name of the local folder you want to monitor 

![monitor_dir](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/monitored_dir_config.png)

- create these folders. 

![folders](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/create_folders.png)

- to run this manually you can hit shift+f10 in file_server and observer or click the green run button.
- when file_server runs you will be prompted to grant firewall access, do this or the server will be upsettingly silent. 

![firewall](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/firewall_access.png)

- you can now add, remove, move and rename folders and text files in the monitored dir to your hearts content!
- there are a few integration tests that can be run in the test folder as well.

## aproach
from the get go the most straightforward course of action to get something working appears to be setting up an os dependant directory listener and to use requests to post data to a server and a quick and dirty rest interface for posts that can listen to files being posted to that address.

once that barebones implementation is working, I can tidy things up and start thinking about optimising data transfer, I can probably do something clever hashing the contents of files and checking them on the server before actually posting the files to see if information is new.

## shortcomings
My solution is naive and barebones in many ways, however works as intended in the brief.
I make no attempt at:
- security
- session handling for the client or server
- authentication
- handling anything other than folders and text files
- cmd argument parsing
- state recovery
- git style context tracking

## improvements I would like to make
- migrate the http server to use flask or django. this would afford better file uploading, and security
- functionality to update the entire directory at once, e.g. when the application launches
- creating sessions with the server, to simplify the process of posting file hashes and then the file if needed.
- a simple argparser for running over the command line
- history tracking for the server, logging dumps and an object-oriented linked list of events.

![test results](https://raw.githubusercontent.com/bramreth/simple-file-monitor/main/assets/test_run.gif)
