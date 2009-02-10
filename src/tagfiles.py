#! /usr/bin/env python

import tagger
import sys

assert len(sys.argv) > 1

dbFile = sys.argv[1]

files = sys.stdin.readlines()
for index, f in enumerate(files):
    files[index] = f.strip()

t = tagger.TagCollector(dbFile, files)
t._processFiles()
