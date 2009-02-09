import re

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

class TagCollector:
    def __init__(self, dbFile, fileList):
        self._fileList = fileList
        self._dbFile = dbFile
        self._connect()
        self._processSQL(self._createTableSQL())

    def _connect(self):
        import sqlite3
        self._connection = sqlite3.connect(self._dbFile)

    def _createSQL(self, method, files):
        ret = []
        for f in files:
            ret.append("REPLACE INTO xref VALUES ('%s', '%s', %d)" \
                       % (method, f[0], f[1]))
        return ret

    def _createTableSQL(self):
        return "CREATE TABLE IF NOT EXISTS xref(" \
               "name varchar(512), " \
               "file varchar(512), " \
               "line integer, " \
               "unique (name, file, line))"

    def _processFiles(self):
        for f in self._fileList:
            self._processFile(f)

    def _processFile(self, fileName):
        t = Tagger()
        occurrences = t.process(fileName)
        if occurrences is None:
            return
        sql = []
        for method, files in occurrences.items():
            sql.extend(self._createSQL(method, files))
        self._processSQL(sql)

    def _processSQL(self, sql):
        cursor = self._connection.cursor()
        for row in sql:
            cursor.execute(row)
        self._connection.commit()
        cursor.close()
