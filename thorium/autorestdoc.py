from docutils.statemachine import StringList
from sphinx.ext.autodoc import bool_option, ClassDocumenter, members_option
from sphinx.locale import _


class RestDocumenter(ClassDocumenter):
    # Working under the assumption that we will only have Meta and Params
    # as potential subclasses for now.
    subclasses = {'Params': {}, 'Meta': {}}
    objtype = 'restclass'
    objpath = None
    properties = []
    option_spec = {
        'members': members_option,
        'show-params': bool_option,
        'show-meta': bool_option
    }
    directivetype = 'class'
    output = {}

    def __init__(self, directive, name, indent=''):
        # We are re-using autodoc's ClassDocumenter so call it's __init__
        # method to setup the object for us.
        super().__init__(directive, name, indent)

        self.parse_name()
        self.import_object()
        self.members = self.get_object_members(True)
        self.extract_members()
        self.extend_result()

    def extend_result(self):
        self.extend_result_with_meta_items()
        self.extend_result_with_params_items()
        self.extend_result_with_properties()

    def extract_members(self):
        for member in self.members[1]:
            key, value = member
            # Extract properties
            if not self.special_method(key) and key not in self.subclasses.keys() and self.options.get('members'):
                self.properties.append(member)
            # Extract subclasses
            if key in self.subclasses.keys() and self.get_option(key):
                self.subclasses[key] = {
                    k: v
                    for k, v in value.__dict__.items()
                    if not self.special_method(k)
                }

    def get_option(self, key):
        key = key.lower()
        if 'show' not in key:
            return self.options.get('-'.join(['show', key]), False)
        return self.options.get(key, False)

    def extend_result_with_properties(self):
        for prop in self.properties:
            self.directive.result.append(
                StringList([
                    '**Property**: ',
                    _(str(prop[0])),
                    '-',
                    _(str(prop[1].__class__)),
                    '\n'
                ])
            )

    def extend_result_with_meta_items(self):
        for k, v in self.subclasses['Meta'].items():
            self.directive.result.append(
                StringList([
                    '**Endpoint**: ',
                    _(self.endpoint_to_str(v['endpoint'])),
                    '-',
                    _(self.methods_to_str(v['methods'])),
                    '\n'])
            )

    def extend_result_with_params_items(self):
        for k, v in self.subclasses['Params'].items():
            self.directive.result.append(
                StringList([
                    '**Querystring Param**: ',
                    _(k),
                    '-',
                    _(str(v.__class__)),
                    '\n'
                ])
            )

    @staticmethod
    def endpoint_to_str(endpoint):
        # Emphasize variables in endpoint URLS
        return endpoint.replace('<', '**<').replace('>', '>**')

    @staticmethod
    def methods_to_str(methods):
        # Italicize HTTP methods
        methods = ['*' + m + '*' for m in methods]
        return ', '.join(methods)

    @staticmethod
    def get_key_for_meta_id(var):
        return var.replace('_methods', '').replace('_endpoint', '')

    @staticmethod
    def special_method(key):
        return key.startswith('__') and key.endswith('__')

def setup(app):
    app.add_autodocumenter(RestDocumenter)
