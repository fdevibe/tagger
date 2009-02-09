import unittest

class OrderTestCase(unittest.TestCase):
    def _classMember(self, theClass, member):
        if member.__name__ in theClass.__dict__:
            return (theClass, theClass.__dict__[member.__name__])
        if len(theClass.__bases__) > 0:
            for base in theClass.__bases__:
                attempt = self._classMember(base, member)
                if attempt is not None:
                    return attempt
        return None

    class Overrider:
        def __init__(self, calledName, methodList):
            self._methodList = methodList
            self._calledName = calledName

        def __call__(self, *args):
            self._methodList.append(self._calledName)

    def _getOriginalMethods(self, methodList, calledMethods):
        ret = []
        for method in methodList:
            (cl, member) = self._classMember(method.im_class, method)
            ret.append((cl, member))
            cl.__dict__[method.__name__] = self.Overrider(method, calledMethods)
        return ret

    def _resetMethods(self, methodList, originalMethods):
        for index, method in enumerate(methodList):
            (cl, member) = originalMethods[index]
            cl.__dict__[method.__name__] = member

    def _callMethod(self, methodToCall, *args, **kwargs):
        if methodToCall.im_self is None:
            if methodToCall.im_func.func_name == '__init__':
                methodToCall.im_class(*args, **kwargs)
            else:
                methodToCall(methodToCall.im_class(), *args, **kwargs)
        else:
            methodToCall(*args, **kwargs)

    def joinList(self, separator, lst):
        if len(lst) > 0 and type(lst[0]).__name__ == 'instancemethod':
            ret = []
            for method in lst:
                ret.append(method.__name__)
            return separator.join(ret)
        elif len(lst) > 0:
            self.assertEquals('str', type(lst[0]).__name__)
        return separator.join(lst)

    def assertOrder(self, methodToCall, methodList, *args, **kwargs):
        theClass = methodToCall.im_class
        calledMethods = []
        originalMethods = self._getOriginalMethods(methodList, calledMethods)
        self._callMethod(methodToCall, *args, **kwargs)
        self._resetMethods(methodList, originalMethods)
        self.assertEquals(
            methodList,
            calledMethods,
            msg = "Expected order '%s', got '%s'" % \
            (self.joinList(' -> ', methodList),
            self.joinList(' -> ', calledMethods)))

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

class TestOrderTestCase(OrderTestCase):
    def testZoot(self):
        o = OrderTest()
        self.assertOrder(o.zoot, [OrderTest.foo, OrderTest.bar, OrderTest.baz])
        self.assertRaises(
            AssertionError,
            self.assertOrder,
            o.zoot,
            [OrderTest.bar, OrderTest.foo, OrderTest.baz])
        self.assertRaises(
            AssertionError,
            self.assertOrder,
            o.zoot,
            [OrderTest.bar, OrderTest.foo, OrderTest.baz])

    def testXyzzy(self):
        o = OrderTest()
        l = [OrderTest.foo, OrderTest.bar, OrderTest.baz]
        self.assertOrder(
            o.xyzzy, l, None)

    def testAssertMessage(self):
        o = OrderTest()
        expected = [OrderTest.bar, OrderTest.foo, OrderTest.baz]
        actual = [OrderTest.foo, OrderTest.bar, OrderTest.baz]
        try:
            self.assertOrder(o.zoot, expected)
        except AssertionError, output:
            self.assertEquals(
                "Expected order '%s', got '%s'" % \
                (self.joinList(' -> ', expected),
                self.joinList(' -> ', actual)),
                output.__str__())

    def testCtor(self):
        self.assertOrder(OrderTest.__init__, [])

    def testOneCall(self):
        self.assertOrder(OrderTest.blatti, [OrderTest.foo])

    def testOneCallFromCtor(self):
        class Foo(OrderTest):
            def __init__(self):
                self.foo()
        self.assertOrder(Foo.__init__, [OrderTest.foo])

    def testDistantParent(self):
        class Foo:
            def foo(self):
                pass
        class Bar(Foo):
            pass
        class Baz(Bar):
            def bar(self):
                self.foo()
        b = Baz()
        self.assertOrder(b.bar, [Baz.foo])

    def testMethodIsStillCallableAfterAssertOrder(self):
        class Foo:
            def foo(self):
                pass
            def bar(self):
                self.foo()
        foo = Foo()
        foo.bar()
        self.assertOrder(foo.bar, [Foo.foo])
        foo.bar()

    def testParentsMethodsAreCorrectlyReset(self):
        class B:
            def b(self):
                pass
        class D(B):
            def d(self):
                self.b()
        d = D()
        self.failIf(D.__dict__.has_key('b'))
        self.assertOrder(d.d, [D.b])
        self.failIf(D.__dict__.has_key('b'))

    def testCallsInOtherClasses(self):
        class A:
            def a(self):
                pass
        class B:
            def b(self):
                A().a()
        b = B()
        self.assertOrder(b.b, [A.a])

    def testBaseClassIsNotBroken(self):
        class B:
            def b(self):
                pass
        class D(B):
            def d(self):
                self.b()
        d = D()
        original = B.b
        self.assertOrder(d.d, [D.b])
        self.assertEquals(original, B.b)

if __name__ == '__main__':
    unittest.main()
