#! /usr/bin/python

import sys
sys.path.append('..')
from tagger import *
import unittest
from StringIO import StringIO

class OrderTestCase(unittest.TestCase):
    def assertExistence(self, theClass, methodList):
        for method in methodList:
            self.assertTrue(
                method in theClass.__dict__,
                msg = '%s.%s() does not exist' % (theClass.__name__, method))

    class Overrider:
        def __init__(self, calledName, methodList):
            self._methodList = methodList
            self._calledName = calledName

        def __call__(self, *args):
            self._methodList.append(self._calledName)

    def assertOrder(self, methodToCall, methodList, *args, **kwargs):
        theClass = methodToCall.im_class
        self.assertExistence(theClass, methodList)
        originalMethods = []
        calledMethods = []
        for method in methodList:
            originalMethods.append(theClass.__dict__[method])
            theClass.__dict__[method] = self.Overrider(method, calledMethods)
        methodToCall(*args, **kwargs)
        for index, method in enumerate(methodList):
            theClass.__dict__[method] = originalMethods[index]
        self.assertEquals(
            methodList,
            calledMethods,
            msg = "Expected order '%s', got '%s'" %\
            (' -> '.join(methodList), ' -> '.join(calledMethods)))

class OrderTest:
    def foo(self):
        pass
    def bar(self):
        pass
    def baz(self):
        pass
    def zoot(self):
        self.foo()
        self.bar()
        self.baz()
    def xyzzy(self, fnutti):
        self.foo()
        self.bar()
        self.baz()

class TestOrderTestCase(OrderTestCase):
    def testZoot(self):
        o = OrderTest()
        self.assertOrder(o.zoot, ['foo', 'bar', 'baz'])
        self.assertRaises(
            AssertionError, self.assertOrder, o.zoot, ['bar', 'foo', 'baz'])
        self.assertRaises(
            AssertionError, self.assertOrder, o.zoot, ['bar', 'foo', 'baz'])

    def testXyzzy(self):
        o = OrderTest()
        self.assertOrder(o.xyzzy, ['foo', 'bar', 'baz'], None)

    def testAssertMessage(self):
        o = OrderTest()
        expected = ['bar', 'foo', 'baz']
        actual = ['foo', 'bar', 'baz']
        try:
            self.assertOrder(o.zoot, expected)
        except AssertionError, output:
            self.assertEquals(
                "Expected order '%s', got '%s'" % \
                (' -> '.join(expected), ' -> '.join(actual)),
                output.__str__())

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

class TaggerTestWithFile(unittest.TestCase):
    def setUp(self):
        self.tagger = Tagger()
        self.originalFile = file
        __builtins__.__dict__['file'] = TestFileDescriptor

    def tearDown(self):
        __builtins__.__dict__['file'] = self.originalFile

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
