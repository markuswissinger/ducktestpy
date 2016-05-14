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

import os
import sys

from ducktest.config_reader import Configuration
from ducktest.docstring_writer import DocstringWriter
from ducktest.typer import run


def main():
    """Script entry point"""
    given_config_file_path = sys.argv[1]
    if os.path.isabs(given_config_file_path):
        config_file_path = given_config_file_path
    else:
        config_file_path = os.path.join(os.getcwd(), given_config_file_path)

    configuration = Configuration.from_file_path(config_file_path)

    typing_debugger = run(configuration)

    DocstringWriter(typing_debugger).write_all()
