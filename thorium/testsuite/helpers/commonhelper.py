import inspect


class Stub(object):

    def __init__(self, cls, pass_methods=[]):
        method_tuples = inspect.getmembers(cls, predicate=inspect.ismethod)
        for name, method in method_tuples:
            self.add_method_stub(method, pass_methods)

    @classmethod
    def add_method_stub(cls, method, pass_methods):
        def new_method(self, *args, **kwargs):
            if method.__name__ in pass_methods:
                pass
            else:
                raise ReachedMethod(method, *args, **kwargs)
        new_method.__name__ = method.__name__
        setattr(cls, method.__name__, new_method)


class ReachedMethod(Exception):

    def __init__(self, method, *args, **kwargs):
        self.method = method

    def expected(self, exp_method):
        if self.method != exp_method:
            raise UnexpectedMethod(exp_method, self.method)
        return True

    def __str__(self):
        return "Reached {rch_cls}:{rch_method} of a Stub object".format(
            rch_cls=self.method.im_class.__name__,
            rch_method=self.method.__name__
        )


class UnexpectedMethod(Exception):

    def __init__(self, exp_method, rch_method):
        self.exp_method = exp_method
        self.rch_method = rch_method

    def __str__(self):
        return "Expected {exp_cls}:{exp_method}, reached {rch_cls}:{rch_method}".format(
            exp_cls=self.exp_method.im_class.__name__,
            exp_method=self.exp_method.__name__,
            rch_cls=self.rch_method.im_class.__name__,
            rch_method=self.rch_method.__name__
        )
