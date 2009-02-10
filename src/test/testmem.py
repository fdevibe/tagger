#! /usr/bin/python

import time
import sqlite3
import sys

conn = sqlite3.connect('dbfile.old')
c = conn.cursor()
c.execute('SELECT file, line FROM xref')

class FileName:
    def __init__(self, name):
        self.name = name

if len(sys.argv) > 1 and sys.argv[1] == 'str':
    l = []
    for row in c:
        l.append((row[0], row[1]))
    print 'done, sleeping 10'
    time.sleep(10)
else:
    l = []
    d = {}
    for row in c:
        if not d.has_key(row[0]):
            d[row[0]] = FileName(row[0])
        l.append((d[row[0]], row[1]))
    print 'done, sleeping 10'
    time.sleep(10)

