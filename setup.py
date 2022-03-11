#!/usr/bin/env python
from __future__ import print_function

import os
import sys

from Cython.Build import cythonize
from setuptools import setup, find_packages, Extension

PACKAGE = 'basex'
NAME = 'basex'
PY_VER = sys.version_info
REQUIREMENTS = [
    'orjson',
    'loguru',
    'PyYAML',
    'pybase64',
    'pydantic',
    'dynaconf',
    'sqlalchemy[asyncio]>=1.4'
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


def get_extensions():
    extensions = []
    for file in os.listdir('basex/native'):
        if file.endswith('.pyx'):
            module_name = file.removesuffix(".pyx")
            modules = [f'basex/native/{file}']
            if os.path.exists(f'basex/native/lib/{module_name}.c'):
                modules.append(f'basex/native/lib/{module_name}.c')
            extensions.append(
                Extension(
                    f'basex.native.{module_name}',
                    modules
                )
            )
    return extensions


setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email="408856732@qq.com",
    description=DESCRIBE,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="BSD 2-Clause",
    url="https://github.com/yinziyan1206/x-base",
    packages=packages,
    install_requires=REQUIREMENTS,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    ext_modules=cythonize(
        get_extensions(),
        language_level=3,
        compiler_directives={},
    )
)
