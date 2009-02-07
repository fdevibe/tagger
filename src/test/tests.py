#! /usr/bin/python

import sys
sys.path.append('..')
from tagger import *
import unittest
from StringIO import StringIO
from ordertestcase import OrderTestCase
import __builtin__

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
            IOError, self.tagger._openFile, 'a non-existing file')

class TestFileDescriptor(StringIO):
    def __init__(self, name):
        self.name = name

    def setContents(self, content):
        StringIO.__init__(self, content)

class TaggerTestWithFile(OrderTestCase):
    def setUp(self):
        self.tagger = Tagger()
        self.originalFile = file
        __builtin__.__dict__['file'] = TestFileDescriptor

    def tearDown(self):
        __builtin__.__dict__['file'] = self.originalFile

    def testOpenFile(self):
        self.tagger._openFile('testFile')
        self.assertEquals('testFile', self.tagger._filePointer.name)

    def testTestReadSomeLines(self):
        self.tagger._openFile('testFile')
        self.tagger._filePointer.setContents(
"""#include <iostream>

class Foo {
    void foo() {
        std::ostream << \"Foo.foo() called\" << std::endl;
    }
};""")
        self.tagger._processFile()
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
             self.tagger._map)

    def testProcess(self):
        self.assertOrder(
            self.tagger.process,
            ['_openFile', '_processFile', '_closeFile'],
            None)

    def testCloseFile(self):
        class CloseFileDescriptor(TestFileDescriptor):
            def __init__(self):
                self.closeCalled = False
            def close(self):
                self.closeCalled = True
        fd = CloseFileDescriptor()
        self.tagger._filePointer = fd
        self.tagger._closeFile()
        self.assertTrue(fd.closeCalled)

if __name__ == '__main__':
    unittest.main()
