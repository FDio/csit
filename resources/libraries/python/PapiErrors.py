# Copyright (c) 2018 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""PAPI Errors class file."""

__all__ = ['PapiError', 'PapiInitError', 'PapiJsonFileError','PapiCommandError',
           'PapiCommandInputError']


class PapiError(Exception):
    """Python API error."""
    pass


class PapiInitError(PapiError):
    """This exception is raised when construction of VPP instance failed."""
    pass


class PapiJsonFileError(PapiError):
    """This exception is raised in case of JSON API file error."""
    pass


class PapiCommandError(PapiError):
    """This exception is raised when PAPI command(s) execution failed."""
    pass


class PapiCommandInputError(PapiCommandError):
    """This exception is raised when incorrect input of Python API is used."""
    pass
