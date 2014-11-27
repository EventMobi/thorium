from distutils.core import setup

setup(
    name='Thorium',
    version='0.1.38',
    description='A Python framework for RESTful API interfaces in Flask',
    author='Ryan Easterbrook',
    author_email='ryan@eventmobi.com',
    url='https://github.com/EventMobi/thorium',
    packages=['thorium'],
    install_requires=['Flask==0.10.1'],
    license='BSD',
    classifiers=[
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ]
)
