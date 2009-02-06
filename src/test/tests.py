#! /usr/bin/python

import sys
sys.path.append('..')
from tagger import *
import unittest

class SimpleTaggerTest(unittest.TestCase):
    def setUp(self):
        self.tagger = Tagger()

    def testFindWordsInSimpleString(self):
        self.assertEquals(
            set(['String', 'args', 'main', 'public', 'static', 'void']),
            self.tagger.getTokens(
            '  public static void main(String [] args) {'))

    def testIgnoredSymbols(self):
        self.assertEquals(
            set(),
            self.tagger.getTokens('!"@#$%&&/{([)]=?+\\`"^~*\'-:.;,<>|'))

    def testDuplicatedSymbols(self):
        self.assertEquals(
            set(['bar', 'zoot']),
            self.tagger.getTokens('zoot zoot bar'))

    def testWhitespace(self):
        self.assertEquals(
            set(),
            self.tagger.getTokens('      '))

    def testAddNonExistingFile(self):
        self.assertRaises(
            IOError, self.tagger.openFile, 'a non-existing file')

class TestFileDescriptor:
    def __init__(self, name):
        self.name = name

    def setContents(self, content):
        self._lines = content
        self._lines.reverse()

    def readline(self):
        return self._lines.pop()

    def __iter__(self):
        return self

    def next(self):
        try:
            return self.readline()
        except IndexError:
            raise StopIteration

class TaggerTestWithFile(unittest.TestCase):
    def setUp(self):
        self.tagger = Tagger()
        self.originalFile = file
        __builtins__.__dict__['file'] = TestFileDescriptor

    def tearDown(self):
        __builtins__.__dict__['file'] = self.originalFile

    def testTestFileDescriptor(self):
        self.tagger.openFile('testFile')
        self.assertEquals('testFile', self.tagger._filePointer.name)

    def testTestReadSomeLines(self):
        self.tagger.openFile('testFile')
        self.tagger._filePointer.setContents(
            ["#include <iostream>\n",
             "\n",
             "class Foo {\n",
             "    void foo() {\n",
             "        std::ostream << \"Foo.foo() called\" << std::endl;\n",
             "    }\n",
             "};\n"])
        self.assertEquals(
            {'Foo': [('testFile', 3), ('testFile', 5)],
             'called': [('testFile', 5)],
             'class': [('testFile', 3)],
             'endl': [('testFile', 5)],
             'foo': [('testFile', 4), ('testFile', 5)],
             'include': [('testFile', 1)],
             'iostream': [('testFile', 1)],
             'ostream': [('testFile', 5)],
             'std': [('testFile', 5)],
             'void': [('testFile', 4)]},
            self.tagger.processFile())

if __name__ == '__main__':
    unittest.main()
