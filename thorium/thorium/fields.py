import calendar


class ResourceField(object):

    def __init__(self):
        self.value = None

    def set(self, value):
        self.value = value


class CharField(ResourceField):
    pass


class IntField(ResourceField):
    pass


class DateTimeField(ResourceField):

    def set(self, value):
        self.value = calendar.timegm(value.timetuple())


class BoolField(ResourceField):
    pass