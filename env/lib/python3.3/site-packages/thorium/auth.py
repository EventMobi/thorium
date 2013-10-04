from . import errors


def use(*authenticator_classes):
    """ A decorator to attach one or more :class:`Authenticator`'s to the decorated class.

    Usage:
        from thorium import auth

        @auth.use(BasicAuth, CustomAuth)
        class MyEngine(Engine):
            ...

        OR

        @auth.use(BasicAuth)
        @auth.use(CustomAuth)
        class MyEngine(Engine):
            ...

    :param authenticator_classes: One or more :class:`Authenticator` class definitions.
    """
    def wrapped(cls):
        if not cls._authenticator_classes:
            cls._authenticator_classes = []
        cls._authenticator_classes.extend(authenticator_classes)
        return cls
    return wrapped


def validation(func):
    """ A simple decorator which marks a method within an :class:`Authenticator` as a
    validation method. All such methods will be converted into decorators via
    the :class:`AuthenticatorMetaClass`. """
    func.is_validation_method = True
    return func


class AuthenticatorMetaClass(type):
    """ Metaclass for :class:`Authenticator`, finds all validation methods within
    the Authenticator and converts them to classmethod decorators which can be used
    on an :class:`Engine`'s methods.
    """

    def __new__(mcs, cls_name, bases, attrs):
        for name, method in attrs.items():
            if hasattr(method, 'is_validation_method'):
                attrs[name] = classmethod(mcs._generate_decorator(method))

        #dynamic creation used so that subclasses don't share these attributes
        attrs['_no_auth_methods'] = set()
        attrs['_validators'] = {}

        return super().__new__(mcs, cls_name, bases, attrs)

    @staticmethod
    def _generate_decorator(validation_method):
        """ Dynamically creates a decorator that will map the decorated
        method to the validation_method.

        :param validation_method: The method with validation rules
        """
        def decorator(cls, func):
            if func not in cls._validators:
                cls._validators[func] = []
            cls._validators[func].append(validation_method)
            return func
        return decorator


class Authenticator(object, metaclass=AuthenticatorMetaClass):
    """ Inherit from this class to create a custom authenticator.

    :param request: A :class:`Request` object.
    """
    def __init__(self, request):
        self._loaded = False
        self.request = request

    @classmethod
    def no_auth(cls, func):
        """ A special validation decorator which indicates that :function:`authentication`
        should not be called for the decorated method.
        """
        cls._no_auth_methods.add(func)
        return func

    def check_auth(self, method):
        """ Finds and executes all validation rules for the given method.

        :param method: A reference to a class method to run validation on.
        """

        method_def = method.__func__
        if method_def not in self._no_auth_methods:
            self.try_load()
            if not self._authenticate():
                raise errors.UnauthorizedError()

        if method_def in self._validators:
            self.try_load()
            for v in self._validators[method_def]:
                if not v(self):
                    raise errors.ForbiddenError()

        return True

    def try_load(self):
        """ Call the :function:`load` subclass hook if it hasn't not already been called. """
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self):
        """ This method will be called only once immediately before running the first validation method.
        Overriding this method is the preferred way to initiate authenticator data since __init__
        will be called whether validation is required or not. """
        pass

    def _authenticate(self):
        """ This method will always be called from :function:`check_auth` except in the case
        where the method being validated has the :function:`no_auth` decorator. Override to
        provide the default authentication check. A False return will throw a access denied
        error. """
        raise NotImplementedError('No authenticator found.')