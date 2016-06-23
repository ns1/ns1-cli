import os
import sys

from ns1cli.version import VERSION

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ns1cli'))

setup(
    name='ns1cli',
    version=VERSION,
    description='NS1 command line interface',
    author='Shannon Weyrick',
    author_email='sweyrick@ns1.com',
    url='https://ns1.com/',
    packages=['ns1cli', 'ns1cli.commands'],
    scripts=['bin/ns1'],
    entry_points={
        'console_scripts': [
            'ns1=ns1cli.cli:main'
        ],
    },
    install_requires=[
        'docopt==0.6.1',
        'nsone==0.9.2',
    ],
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest',
        'pytest-mock',
        'pytest-pep8',
        'pytest-cov',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'Intended Audience :: System Administrators',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
    ])
