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

    def processFile(self, filename):
        self._filePointer = file(filename)
