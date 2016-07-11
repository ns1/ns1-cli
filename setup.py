from ns1cli import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ns1cli',
    version=__version__,
    description='NS1 command line interface',
    author='Shannon Weyrick',
    author_email='sweyrick@ns1.com',
    url='https://ns1.com/',
    packages=['ns1cli', 'ns1cli.commands'],
    include_package_date=True,
    entry_points={
        'console_scripts': [
            'ns1=ns1cli.cli:cli'
        ],
    },
    install_requires=[
        'click==6.6',
        'nsone>=0.9.4',
        'requests',
        'six'
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
