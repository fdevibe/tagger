#! /usr/bin/python

import sys
sys.path.append('..')
from tagger import *
import unittest

class TaggerTest(unittest.TestCase):
    def setUp(self):
        self.tagger = Tagger()

    def testFindWordsInSimpleString(self):
        actual = list(self.tagger.getTokens(
            '  public static void main(String [] args) {'))
        actual.sort()
        self.assertEquals(
            ['String', 'args', 'main', 'public', 'static', 'void'],
            actual)

    def testIgnoredSymbols(self):
        self.assertEquals(
            set(),
            self.tagger.getTokens('!"@#$%&&/{([)]=?+\\`"^~*\'-:.;,<>|'))

    def testDuplicatedSymbols(self):
        actual = list(self.tagger.getTokens('zoot zoot bar'))
        actual.sort()
        self.assertEquals(['bar', 'zoot'], actual)

class FileTaggerTest(unittest.TestCase):
    def testAddNonExistingFile(self):
        self.assertRaises(IOError, FileTagger, 'a non-existing file')

if __name__ == '__main__':
    unittest.main()
