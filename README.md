# simple-file-monitor
barebones python file management system

## specification

Build an application to synchronise a source folder and a destination folder over IP:

- 1.1 a simple command line client which takes one directory as argument and keeps
monitoring changes in that directory and uploads any change to its server

- 1.2 a simple server which takes one empty directory as argument and receives any change
from its client
- Bonus 1. optimise data transfer by avoiding uploading the same file multiple times
- Bonus 2. optimise data transfer by avoiding uploading the same partial files (files sharing
partially the same content) multiple times

## aproach
from the get go the most straightforward course of action to get something working appears to be setting up an os dependant directory listener and to use requests to post data to a server and a quick and dirty rest interface for posts that can listen to files being posted to that address.

once that barebones implementation is working, I can tidy things up and start thinking about optimising data transfer, I can probably do something clever hashing the contents of files and checking them on the server before actually posting the files to see if information is new.
