#!/usr/bin/env python
from __future__ import print_function

import sys

from Cython.Build import cythonize
from setuptools import setup, find_packages, Extension

PACKAGE = 'basex'
NAME = 'basex'
PY_VER = sys.version_info
REQUIREMENTS = [
    'polars',
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
    'Intended Audience :: Developers',
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    'Operating System :: OS Independent',
    'Environment :: Web Environment',
    'Development Status :: 3 - Alpha',
    'Topic :: Internet',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

KEYWORDS = ["api", "x-api", "x-base", "basex"]
packages = find_packages()


setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email="408856732@qq.com",
    description=DESCRIBE,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="BSD 2-Clause",
    url=f"https://github.com/yinziyan1206/x-base",
    packages=packages,
    install_requires=REQUIREMENTS,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    ext_modules=cythonize(
        [
            Extension('basex.common.cryptutils', ['basex/common/cryptutils.py']),
            Extension('basex.common.objectutils', ['basex/common/objectutils.py']),
            Extension('basex.common.stringutils', ['basex/common/stringutils.py']),
            Extension('basex.config.content', ['basex/config/content.py']),
            Extension('basex.db.sequence', ['basex/db/sequence.py'])
        ],
        language_level=3,
        compiler_directives={},
    )
)
