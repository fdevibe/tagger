import re

class Tagger:
    def getTokens(self, string):
        tokens = re.split('[\W]*', string)
        return self.removeBlanks(tokens)

    def removeBlanks(self, tokens):
        try:
            while True:
                tokens.remove('')
        except ValueError:
            return tokens

class FileTagger:
    def __init__(self, filename):
        self.fp = open(filename)
