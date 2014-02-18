from distutils.core import setup

setup(name='Thorium',
      version='0.1.14',
      description='A Python framework for simple RESTful API interfaces',
      author='Ryan Easterbrook',
      author_email='ryan@eventmobi.com',
      url='https://github.com/EventMobi/thorium',
      packages=['thorium'],
      install_requires=['Flask==0.10.1']
      )
