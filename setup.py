import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

requests = 'docopt == 0.6.1'
install_requires = [requests]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nsonecli'))
from version import VERSION

setup(
    name='nsonecli',
    version=VERSION,
    description='NSONE command line interface',
    author='Shannon Weyrick',
    author_email='sweyrick@nsone.net',
    url='https://nsone.net/',
    packages=['nsonecli'],
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'Intended Audience :: System Administrators',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        #"Programming Language :: Python :: 3",
        #"Programming Language :: Python :: 3.3",
    ])
