import routing


class Thorium(object):

    def __init__(self, settings):
        self.settings = settings
        self.routes = routing.get_all_routes()

