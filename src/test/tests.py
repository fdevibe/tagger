#! /usr/bin/python
# -*- compile-comand: "make -C /local/src/div/tagger/src/test" -*-

import sys
sys.path.append('..')
from tagger import *
import unittest

class TaggerTest(unittest.TestCase):
    def setUp(self):
        self.tagger = Tagger()

    def testFindWordsInSimpleString(self):
        self.assertEquals(
            ['public', 'static', 'void', 'main', 'String', 'args'],
            self.tagger.getTokens(
            '  public static void main(String [] args) {'))

    def testIgnoredSymbols(self):
        self.assertEquals(
            [],
            self.tagger.getTokens('!"@#$%&&/{([)]=?+\\`"^~*\'-:.;,<>|'))

class FileTaggerTest(unittest.TestCase):
    def testAddNonExistingFile(self):
        self.assertRaises(IOError, FileTagger, 'a non-existing file')

if __name__ == '__main__':
    unittest.main()
