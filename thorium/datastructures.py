class NotSet(object):

    def __eq__(self, other):
        return (str(self) == str(other)) and not other

    def __bool__(self):
        return False

    def __str__(self):
        return 'NotSet'

    def __repr__(self):
        return 'NotSet'

NotSet = NotSet()
