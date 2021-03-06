"""
Copyright 2016 Markus Wissinger. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import re
from codecs import open
from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = str(f.read())

with open(path.join(here, 'ducktest', 'version.py')) as f:
    first_line = f.readline()
    version = re.match("VERSION = '([^\']+)'", first_line).group(1)

setup(
    name='ducktest',
    version=version,
    description='Generate type hints from unit tests',
    long_description=long_description,
    url='https://github.com/markuswissinger/ducktestpy',
    author='Markus Wissinger',
    author_email='markus.wissinger@gmail.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='development tool type hinting unittest living documentation',
    packages=['ducktest'],
    install_requires=['future', 'mock', ],
)
