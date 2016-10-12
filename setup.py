from setuptools import setup

setup(
    name='Thorium',
    version='0.2.15',
    description='A Python framework for RESTful API interfaces in Flask',
    author='Ryan Easterbrook',
    author_email='ryan@eventmobi.com',
    url='https://github.com/EventMobi/thorium',
    packages=['thorium', 'thorium.ext'],
    install_requires=['Flask==0.10.1', 'jsonschema==2.4.0', 'arrow==0.5.4'],
    license='BSD',
    classifiers=[
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ]
)
