import unittest

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

if __name__ == '__main__':
    unittest.main()
