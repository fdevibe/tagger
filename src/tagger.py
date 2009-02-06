import re

class Tagger:
    def getTokens(self, string):
        tokens = set(re.split('[\W]*', string))
        return self.removeBlanks(tokens)

    def removeBlanks(self, tokens):
        try:
            while True:
                tokens.remove('')
        except KeyError:
            return tokens

    def openFile(self, filename):
        self._filePointer = file(filename)

    def processFile(self):
        ret = {}
        for lineNo, line in enumerate(self._filePointer):
            for token in self.getTokens(line):
                if not ret.has_key(token):
                    ret[token] = []
                ret[token].append((self._filePointer.name, lineNo + 1))
        return ret
