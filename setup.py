#!/usr/bin/env python
from __future__ import print_function

import sys

from setuptools import setup, find_packages

PACKAGE = 'basex'
NAME = 'basex'
PY_VER = sys.version_info
REQUIREMENTS = [
    'orjson',
    'loguru',
    'PyYAML',
    'pydantic',
    'sqlalchemy>=1.4'
]
package = __import__(PACKAGE)
VERSION = package.__version__
AUTHOR = package.__author__
DESCRIBE = package.__describe__

CLASSIFIERS = [
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Operating System :: ALL',
    'Environment :: Web Environment',
    'Development Status :: 3 - Alpha',
    'Topic :: Restful API',
    'Topic :: Restful API :: Back-Ends',
    'Framework :: FastApi',
]

KEYWORDS = ["api", "x-api", "basex"]

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email="408856732@qq.com",
    description=DESCRIBE,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url=f"https://github.com/yinziyan1206/{PACKAGE}",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS
)
