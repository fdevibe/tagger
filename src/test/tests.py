#! /usr/bin/python

import sys
sys.path.append('..')
from tagger import *
import unittest

class SimpleTaggerTest(unittest.TestCase):
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

    def testWhitespace(self):
        self.assertEquals(
            set(),
            self.tagger.getTokens('      '))

    def testAddNonExistingFile(self):
        self.assertRaises(
            IOError, self.tagger.processFile, 'a non-existing file')

class TestFileDescriptor:
    def __init__(self, name):
        self.name = name

    def setContents(self, content):
        self._lines = content
        self._lines.reverse()

    def readline(self):
        return _lines.pop()

class TaggerTestWithFile(unittest.TestCase):
    def setUp(self):
        self.tagger = Tagger()
        self.originalFile = file
        __builtins__.__dict__['file'] = TestFileDescriptor

    def tearDown(self):
        __builtins__.__dict__['file'] = self.originalFile

    def testTestFileDescriptor(self):
        self.tagger.processFile('testFile')
        self.assertEquals('testFile', self.tagger._filePointer.name)

if __name__ == '__main__':
    unittest.main()
