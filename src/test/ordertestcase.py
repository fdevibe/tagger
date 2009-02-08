import unittest

class OrderTestCase(unittest.TestCase):
    def _classMember(self, theClass, member):
        if member in theClass.__dict__:
            return theClass.__dict__[member]
        if len(theClass.__bases__) > 0:
            for base in theClass.__bases__:
                attempt = self._classMember(base, member)
                if attempt is not None:
                    return attempt
        return None

    def assertExistence(self, theClass, methodList):
        for method in methodList:
            self.assertTrue(
                self._classMember(theClass, method) != None,
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
            # originalMethods.append(theClass.__dict__[method])
            originalMethods.append(self._classMember(theClass, method))
            theClass.__dict__[method] = self.Overrider(method, calledMethods)
        if methodToCall.im_self is None:
            if methodToCall.im_func.func_name == '__init__':
                methodToCall.im_class(*args, **kwargs)
            else:
                methodToCall(methodToCall.im_class(), *args, **kwargs)
        else:
            methodToCall(*args, **kwargs)
        for index, method in enumerate(methodList):
            theClass.__dict__[method] = originalMethods[index]
        self.assertEquals(
            methodList,
            calledMethods,
            msg = "Expected order '%s', got '%s'" %\
            (' -> '.join(methodList), ' -> '.join(calledMethods)))

class OrderTest:
    def __init__(self):
        pass
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
    def blatti(self):
        self.foo()

class OrderTestCallingMemberInCtor(OrderTest):
    def __init__(self):
        self.foo()

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

    def testCtor(self):
        self.assertOrder(OrderTest.__init__, [])

    def testOneCall(self):
        self.assertOrder(OrderTest.blatti, ['foo'])

    def testOneCallFromCtor(self):
        self.assertOrder(OrderTestCallingMemberInCtor.__init__, ['foo'])

    def testDistantParent(self):
        class Foo:
            def foo(self):
                pass
        class Bar(Foo):
            pass
        class Baz(Bar):
            pass
        self.assertExistence(Baz, ['foo'])

    def testMethodIsStillCallableAfterAssertOrder(self):
        class Foo:
            def foo(self):
                pass
            def bar(self):
                self.foo()
        foo = Foo()
        foo.bar()
        self.assertOrder(foo.bar, ['foo'])
        foo.bar()

if __name__ == '__main__':
    unittest.main()