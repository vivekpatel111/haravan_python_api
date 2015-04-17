from setuptools import setup

NAME='HaravanAPI'
exec(open('haravan/version.py').read())
DESCRIPTION='Haravan API for Python'
LONG_DESCRIPTION="""\
The HaravanAPI library allows python developers to programmatically
access the admin section of stores using an ActiveResource like
interface similar the ruby Haravan API gem. The library makes HTTP
requests to Haravan in order to list, create, update, or delete
resources (e.g. Order, Product, Collection)."""

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author='Haravan',
      author_email='developers@haravan.com',
      url='https://github.com/Haravan/haravan_python_api',
      packages=['haravan', 'haravan/resources'],
      scripts=['scripts/haravan_api.py'],
      license='MIT License',
      install_requires=[
          'pyactiveresource>=2.1.1',
          'PyYAML',
          'six',
      ],
      test_suite='test',
      tests_require=[
        'mock>=1.0.1',
      ],
      platforms='Any',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Topic :: Software Development',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Software Development :: Libraries :: Python Modules']
      )
