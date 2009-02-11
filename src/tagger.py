import re
import sys
import sqlite3

class Tagger:
    def __init__(self):
        self._map = None

    def getTokens(self, string):
        tokens = set(re.split('[\W]*', string))
        return self.removeBlanks(tokens)

    def removeBlanks(self, tokens):
        if '' in tokens:
            tokens.remove('')
        return tokens

    def _openFile(self, filename):
        self._filePointer = file(filename)

    def _processFile(self):
        self._map = {}
        for lineNo, line in enumerate(self._filePointer):
            for token in self.getTokens(line):
                if not self._map.has_key(token):
                    self._map[token] = []
                self._map[token].append((self._filePointer.name, lineNo + 1))

    def _closeFile(self):
        self._filePointer.close()

    def process(self, filename):
        self._openFile(filename)
        self._processFile()
        self._closeFile()
        return self._map

class FileName:
    def __init__(self, name):
        self.name = name

class TagCollector:
    def __init__(self, dbFile, fileList):
        self._fileList = fileList
        self._dbFile = dbFile
        self._connect()
        self._processSQL(self._createTableSQL(64, 128))
        self._map = {}
        self._files = {}

    def _connect(self):
        self._connection = sqlite3.connect(self._dbFile)

    def _createTableSQL(self, symbolLength, fileNameLength):
        return ["CREATE TABLE IF NOT EXISTS symbols(" \
                "ID INTEGER PRIMARY KEY, " \
                "symbol varchar(%d))" % symbolLength,
                "CREATE TABLE IF NOT EXISTS files(" \
                "ID INTEGER PRIMARY KEY, " \
                "file varchar(%d))" % fileNameLength,
                "CREATE TABLE IF NOT EXISTS xref(" \
                "symbol INTEGER, " \
                "file INTEGER, " \
                "line INTEGER)"
                ]

    def _processFiles(self):
        for f in self._fileList:
            try:
                self._processFile(f)
            except IOError:
                sys.stderr.write("Warning: %s: No such file\n" % f)
                continue
        self._processInsertSQL()

    def _processFile(self, fileName):
        if self._files.has_key(fileName):
            return
        self._files[fileName] = FileName(fileName)
        t = Tagger()
        occurrences = t.process(fileName)
        if occurrences is None:
            return
        for symbol, files in occurrences.items():
            self._addToMap(symbol, files)

    def _addToMap(self, symbol, files):
        if not self._map.has_key(symbol):
            self._map[symbol] = []
        for f, line in files:
            self._map[symbol].append((self._files[f], line))

    def _processSQL(self, sql):
        cursor = self._connection.cursor()
        for row in sql:
            cursor.execute(row)
        self._connection.commit()
        cursor.close()

    def _processInsertSQL(self):
        print 'Processing SQL... (%s symbols)' % len(self._map)
        cursor = self._connection.cursor()
        for symbol, files in self._map.items():
            for fileName, line in files:
                cursor.execute(
                    "INSERT INTO xref VALUES (?, ?, ?)",
                    (symbol, fileName.name, line))
        self._connection.commit()
        cursor.close()
