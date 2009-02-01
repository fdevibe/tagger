#! /usr/bin/python
# -*- compile-comand: "make -C ~/src/tagger/src/test" -*-

import sys
sys.path.append('..')
from tagger import Tagger
import unittest

class TagsTest(unittest.TestCase):
    def testFindWordsInSimpleString(self):
        t = Tagger()
        self.assertEquals(
            ['public', 'static', 'void', 'main', 'String', 'args'],
            t.parseString('  public static void main(String [] args) {'))

if __name__ == '__main__':
    unittest.main()
