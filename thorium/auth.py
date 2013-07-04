
def use(authenticator_class):
    """ A decorator to attach a :class:`Authenticator` """
    def wrapped(cls):
        if not cls._authenticator_classes:
            cls._authenticator_classes = []
        cls._authenticator_classes.append(authenticator_class)
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
        method_def = method.__func__
        if method_def not in self._no_auth_methods:
            self.try_load()
            if not self.authenticate():
                raise Exception('Failed auth')

        if method_def in self._validators:
            self.try_load()
            for v in self._validators[method_def]:
                if not v(self):
                    raise Exception('failed validation')

        return True

    def try_load(self):
        if not self._loaded:
            self.load()

    def load(self):
        pass

    def authenticate(self):
        raise NotImplementedError('No authenticator found.')