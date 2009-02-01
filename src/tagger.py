import re

class Tagger:
    def parseString(self, string):
        tokens = re.split('[ \[\](){]*', string)
        return self.removeBlanks(tokens)

    def removeBlanks(self, tokens):
        try:
            while True:
                tokens.remove('')
        except ValueError:
            return tokens
