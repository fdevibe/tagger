#! /usr/bin/python

import sys
sys.path.append('..')
from tagger import *
import unittest
from StringIO import StringIO
from ordertestcase import OrderTestCase
import __builtin__
import tagger

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
        StringIO.__init__(self, '')

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
            [Tagger._openFile, Tagger._processFile, Tagger._closeFile],
            None)
        self.assertEquals({}, self.tagger.process('testFile'))

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

class TestTagCollector(TagCollector):
    def _connect(self):
        pass
    def _processSQL(self, sql):
        pass

class TagCollectorTest(OrderTestCase):
    def testInitCalls(self):
        self.assertOrder(
            TagCollector.__init__,
            [TagCollector._connect, TagCollector._processSQL],
            None, None)

    def testInitSetsList(self):
        l = ['foo', 'bar']
        tc = TestTagCollector(None, l)
        self.assertEquals(tc._fileList, l)

    def testCreateSQL(self):
        tc = TestTagCollector(None, None)
        method = 'foo'
        files = [('bar', 13), ('baz', 54)]
        self.assertEquals(
            ["REPLACE INTO xref VALUES ('%s', '%s', %d)" \
             % (method, files[0][0], files[0][1]),
             "REPLACE INTO xref VALUES ('%s', '%s', %d)" \
             % (method, files[1][0], files[1][1])],
            tc._createSQL(method, files))

    def testInitSetsDBFile(self):
        dbFile = 'zoot'
        tc = TestTagCollector(dbFile, None)
        self.assertEquals(tc._dbFile, dbFile)

    def testProcessFiles(self):
        processed = []
        class TestTC(TestTagCollector):
            def __init__(self, fileList):
                TagCollector.__init__(self, 'zoot', fileList)
            def _processFile(self, fileName):
                processed.append(fileName)
        l = ['foo', 'bar']
        tc = TestTC(l)
        tc._processFiles()
        self.assertEquals(l, processed)

    def testProcessFile(self):
        tc = TestTagCollector(None, None)
        self.assertOrder(
            tc._processFile,
            [Tagger.__init__, Tagger.process],
            None)

    def testCreateTable(self):
        self.assertEquals(
            ["CREATE TABLE IF NOT EXISTS xref(" \
             "name varchar(512), " \
             "file varchar(512), " \
             "line integer, " \
             "unique (name, file, line))"],
            TestTagCollector(None, None)._createTableSQL())

    def testNonExistingFileShouldntRaiseIOError(self):
        tc = TestTagCollector(None, ['non-existing file'])
        class DevNull:
            def write(self, what):
                pass
        tmp = sys.stderr
        sys.stderr = DevNull()
        tc._processFiles()
        sys.stderr = tmp

class TestCollectTags(unittest.TestCase):
    def setUp(self):
        self.files = {'fnutti.c': "foo\nbar baz\nbar zoot",
                      'blatti.c': "zoot\nbaz\nxyzzy foo"}
        files = self.files
        self.actual = []
        actual = self.actual
        def fakeProcSQL(self, sql):
            actual.extend(sql)
        def fakeCreateSQL(self, method, files):
            ret = []
            for (fileName, line) in files:
                ret.append((method, fileName, int(line)))
            return ret
        class FakeTagger(tagger.Tagger):
            def _openFile(self, fileName):
                self._filePointer = TestFileDescriptor(fileName)
                self._filePointer.setContents(files[fileName])
        self.collector = TestTagCollector(None, self.files.keys())
        self.tmpProcSQL = TestTagCollector._processSQL
        TestTagCollector._processSQL = fakeProcSQL
        self.tmpCreateSQL = TagCollector._createSQL
        TagCollector._createSQL = fakeCreateSQL
        self.tmpTagger = tagger.Tagger
        tagger.Tagger = FakeTagger

    def tearDown(self):
        tagger.Tagger = self.tmpTagger
        TestTagCollector._processSQL = self.tmpProcSQL
        TagCollector._createSQL = self.tmpCreateSQL

    def testCollectTags(self):
        expected = [
            ('bar', 'fnutti.c', 2),
            ('bar', 'fnutti.c', 3),
            ('foo', 'fnutti.c', 1),
            ('baz', 'fnutti.c', 2),
            ('zoot', 'fnutti.c', 3),
            ('baz', 'blatti.c', 2),
            ('foo', 'blatti.c', 3),
            ('zoot', 'blatti.c', 1),
            ('xyzzy', 'blatti.c', 3)]
        self.collector._processFiles()
        self.assertEquals(expected, self.actual)

    def testProcessFileAddsToInternalMap(self):
        self.collector._processFile('fnutti.c')
        self.assertEquals(
            {'bar': [(self.collector._files['fnutti.c'], 2),
                     (self.collector._files['fnutti.c'], 3)],
             'foo': [(self.collector._files['fnutti.c'], 1)],
             'baz': [(self.collector._files['fnutti.c'], 2)],
             'zoot': [(self.collector._files['fnutti.c'], 3)]},
            self.collector._map)

if __name__ == '__main__':
    unittest.main()
