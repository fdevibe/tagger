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
            IOError, self.tagger._openFile, 'a non-existing file')

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
        self.tagger._openFile('testFile')
        self.assertEquals('testFile', self.tagger._filePointer.name)

    def testTestReadSomeLines(self):
        self.tagger._openFile('testFile')
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
            self.tagger._processFile())

    def testProcess(self):
        assertTrue = self.assertTrue
        failIf = self.failIf
        class ProcessTestTagger(Tagger):
            def __init__(self):
                assertTrue('_openFile' in Tagger.__dict__)
                assertTrue('_processFile' in Tagger.__dict__)
                assertTrue('_closeFile' in Tagger.__dict__)
                self.openFileCalled = False
                self.processFileCalled = False
                self.closeFileCalled = False
            def _openFile(self, name):
                failIf(self.openFileCalled)
                failIf(self.processFileCalled)
                failIf(self.closeFileCalled)
                self.openFileCalled = True
            def _processFile(self):
                assertTrue(self.openFileCalled)
                failIf(self.processFileCalled)
                failIf(self.closeFileCalled)
                self.processFileCalled = True
            def _closeFile(self):
                assertTrue(self.openFileCalled)
                assertTrue(self.processFileCalled)
                failIf(self.closeFileCalled)
                self.closeFileCalled = True
        t = ProcessTestTagger()
        t.process('foo')

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
