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

"""Inputs
Download all data.
"""

import re
import logging

from os import rename
from os.path import join
from shutil import move
from zipfile import ZipFile, is_zipfile, BadZipfile
from httplib import responses
from requests import get, codes, RequestException, Timeout, TooManyRedirects, \
    HTTPError, ConnectionError

from errors import PresentationError
from utils import execute_command

# Chunk size used for file download
CHUNK_SIZE = 512

# Separator used in file names
SEPARATOR = "__"

REGEX_RELEASE = re.compile(r'(\D*)(\d{4}|master)(\D*)')


def _download_file(url, file_name):
    """Download a file with input data.

    :param url: URL to the file to download.
    :param file_name: Name of file to download.
    :type url: str
    :type file_name: str
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    success = False
    try:
        logging.info("      Connecting to '{0}' ...".format(url))

        response = get(url, stream=True)
        code = response.status_code

        logging.info("      {0}: {1}".format(code, responses[code]))

        if code != codes["OK"]:
            return False

        logging.info("      Downloading the file '{0}' to '{1}' ...".
                     format(url, file_name))

        file_handle = open(file_name, "wb")
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                file_handle.write(chunk)
        file_handle.close()
        success = True
    except ConnectionError as err:
        logging.error("Not possible to connect to '{0}'.".format(url))
        logging.debug(str(err))
    except HTTPError as err:
        logging.error("Invalid HTTP response from '{0}'.".format(url))
        logging.debug(str(err))
    except TooManyRedirects as err:
        logging.error("Request exceeded the configured number "
                      "of maximum re-directions.")
        logging.debug(str(err))
    except Timeout as err:
        logging.error("Request timed out.")
        logging.debug(str(err))
    except RequestException as err:
        logging.error("Unexpected HTTP request exception.")
        logging.debug(str(err))
    except (IOError, ValueError, KeyError) as err:
        logging.error("Download failed.")
        logging.debug(str(err))

    logging.info("      Download finished.")
    return success


def _unzip_file(spec, job, build):
    """Unzip downloaded source file.

    :param spec: Specification read form the specification file.
    :param job: Name of the Jenkins job.
    :param build: Information about the build.
    :type spec: Specification
    :type job: str
    :type build: dict
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    data_file = spec.input["extract"]
    file_name = build["file-name"]
    directory = spec.environment["paths"]["DIR[WORKING,DATA]"]
    new_name = "{0}{1}{2}".format(file_name.rsplit('.')[-2],
                                  SEPARATOR,
                                  data_file.split("/")[-1])
    logging.info("      Unzipping: '{0}' from '{1}'.".
                 format(data_file, file_name))
    try:
        with ZipFile(file_name, 'r') as zip_file:
            zip_file.extract(data_file, directory)
        logging.info("      Moving {0} to {1} ...".
                     format(join(directory, data_file), directory))
        move(join(directory, data_file), directory)
        logging.info("      Renaming the file '{0}' to '{1}'".
                     format(join(directory, data_file.split("/")[-1]),
                            new_name))
        rename(join(directory, data_file.split("/")[-1]),
               new_name)
        spec.set_input_file_name(job, build["build"],
                                 new_name)
        return True
    except (BadZipfile, RuntimeError) as err:
        logging.error("Failed to unzip the file '{0}': {1}.".
                      format(file_name, str(err)))
        return False
    except OSError as err:
        logging.error("Failed to rename the file '{0}': {1}.".
                      format(data_file, str(err)))
        return False


def download_and_unzip_data_file(spec, job, build):
    """Download and unzip a source file.

    :param spec: Specification read form the specification file.
    :param job: Name of the Jenkins job.
    :param build: Information about the build.
    :type spec: Specification
    :type job: str
    :type build: dict
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    if job.startswith("csit-"):
        if spec.input["file-name"].endswith(".zip"):
            url = spec.environment["urls"]["URL[JENKINS,CSIT]"]
        elif spec.input["file-name"].endswith(".gz"):
            url = spec.environment["urls"]["URL[NEXUS,LOG]"]
        else:
            logging.error("Not supported file format.")
            return False
    elif job.startswith("hc2vpp-"):
        url = spec.environment["urls"]["URL[JENKINS,HC]"]
    else:
        raise PresentationError("No url defined for the job '{}'.".
                                format(job))
    file_name = spec.input["file-name"]
    full_name = spec.input["download-path"]. \
        format(job=job, build=build["build"], filename=file_name)
    url = "{0}/{1}".format(url, full_name)
    new_name = join(spec.environment["paths"]["DIR[WORKING,DATA]"],
                    "{job}{sep}{build}{sep}{name}".
                    format(job=job, sep=SEPARATOR, build=build["build"],
                           name=file_name))
    # Download the file from the defined source (Jenkins, logs.fd.io):
    success = _download_file(url, new_name)

    # If not successful, download from docs.fd.io:
    if not success:
        logging.info("      Trying to download from https://docs.fd.io:")
        release = re.search(REGEX_RELEASE, job).group(2)
        nexus_file_name = "{job}{sep}{build}{sep}{name}". \
            format(job=job, sep=SEPARATOR, build=build["build"], name=file_name)
        try:
            release = "rls{0}".format(int(release))
        except ValueError:
            pass
        url = "{url}/{release}/{dir}/{file}". \
            format(url=spec.environment["urls"]["URL[NEXUS]"],
                   release=release,
                   dir=spec.environment["urls"]["DIR[NEXUS]"],
                   file=nexus_file_name)
        success = _download_file(url, new_name)

    if success:
        spec.set_input_file_name(job, build["build"], new_name)
    else:
        return False

    if spec.input["file-name"].endswith(".gz"):
        if "docs.fd.io" in url:
            execute_command("gzip --decompress --keep --force {0}".
                            format(new_name))
        else:
            rename(new_name, new_name[:-3])
            execute_command("gzip --keep {0}".format(new_name[:-3]))
        spec.set_input_file_name(job, build["build"], new_name[:-3])

    if spec.input["file-name"].endswith(".zip"):
        if is_zipfile(file_name):
            return _unzip_file(spec, job, build)
        else:
            return False
    else:
        return True
