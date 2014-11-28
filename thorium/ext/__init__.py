# -*- coding: utf-8 -*-
"""
    thorium.ext
    ~~~~~~~~~

    :license: BSD, see LICENSE for more details.
"""


def setup():
    from flask.exthook import ExtensionImporter
    importer = ExtensionImporter(['thorium_%s'], __name__)
    importer.install()


setup()
del setup
