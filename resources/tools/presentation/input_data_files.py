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

from os import rename, mkdir
from os.path import join
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


def _download_file(url, file_name, log):
    """Download a file with input data.

    :param url: URL to the file to download.
    :param file_name: Name of file to download.
    :param log: List of log messages.
    :type url: str
    :type file_name: str
    :type log: list of tuples (severity, msg)
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    success = False
    try:
        log.append(("INFO", "    Connecting to '{0}' ...".format(url)))

        response = get(url, stream=True)
        code = response.status_code

        log.append(("INFO", "    {0}: {1}".format(code, responses[code])))

        if code != codes["OK"]:
            return False

        log.append(("INFO", "    Downloading the file '{0}' to '{1}' ...".
                    format(url, file_name)))

        file_handle = open(file_name, "wb")
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                file_handle.write(chunk)
        file_handle.close()
        success = True
    except ConnectionError as err:
        log.append(("ERROR", "Not possible to connect to '{0}'.".format(url)))
        log.append(("DEBUG", str(err)))
    except HTTPError as err:
        log.append(("ERROR", "Invalid HTTP response from '{0}'.".format(url)))
        log.append(("DEBUG", str(err)))
    except TooManyRedirects as err:
        log.append(("ERROR", "Request exceeded the configured number "
                             "of maximum re-directions."))
        log.append(("DEBUG", str(err)))
    except Timeout as err:
        log.append(("ERROR", "Request timed out."))
        log.append(("DEBUG", str(err)))
    except RequestException as err:
        log.append(("ERROR", "Unexpected HTTP request exception."))
        log.append(("DEBUG", str(err)))
    except (IOError, ValueError, KeyError) as err:
        log.append(("ERROR", "Download failed."))
        log.append(("DEBUG", str(err)))

    log.append(("INFO", "    Download finished."))
    return success


def _unzip_file(spec, build, pid, log):
    """Unzip downloaded source file.

    :param spec: Specification read form the specification file.
    :param build: Information about the build.
    :param log: List of log messages.
    :type spec: Specification
    :type build: dict
    :type log: list of tuples (severity, msg)
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    data_file = spec.input["extract"]
    file_name = build["file-name"]
    directory = spec.environment["paths"]["DIR[WORKING,DATA]"]
    tmp_dir = join(directory, str(pid))
    try:
        mkdir(tmp_dir)
    except OSError:
        pass
    new_name = "{0}{1}{2}".format(file_name.rsplit('.')[-2],
                                  SEPARATOR,
                                  data_file.split("/")[-1])

    log.append(("INFO", "    Unzipping: '{0}' from '{1}'.".
                format(data_file, file_name)))
    try:
        with ZipFile(file_name, 'r') as zip_file:
            zip_file.extract(data_file, tmp_dir)
        log.append(("INFO", "    Renaming the file '{0}' to '{1}'".
                    format(join(tmp_dir, data_file), new_name)))
        rename(join(tmp_dir, data_file), new_name)
        build["file-name"] = new_name
        return True
    except (BadZipfile, RuntimeError) as err:
        log.append(("ERROR", "Failed to unzip the file '{0}': {1}.".
                    format(file_name, str(err))))
        return False
    except OSError as err:
        log.append(("ERROR", "Failed to rename the file '{0}': {1}.".
                    format(data_file, str(err))))
        return False


def download_and_unzip_data_file(spec, job, build, pid, log):
    """Download and unzip a source file.

    :param spec: Specification read form the specification file.
    :param job: Name of the Jenkins job.
    :param build: Information about the build.
    :param pid: PID of the process executing this method.
    :param log: List of log messages.
    :type spec: Specification
    :type job: str
    :type build: dict
    :type pid: int
    :type log: list of tuples (severity, msg)
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    if job.startswith("csit-"):
        if spec.input["file-name"].endswith(".zip"):
            url = spec.environment["urls"]["URL[JENKINS,CSIT]"]
        elif spec.input["file-name"].endswith(".gz"):
            url = spec.environment["urls"]["URL[NEXUS,LOG]"]
        else:
            log.append(("ERROR", "Not supported file format."))
            return False
    elif job.startswith("hc2vpp-"):
        url = spec.environment["urls"]["URL[JENKINS,HC]"]
    elif job.startswith("intel-dnv-"):
        url = spec.environment["urls"]["URL[VIRL,DNV]"]
    else:
        raise PresentationError("No url defined for the job '{}'.".
                                format(job))
    file_name = spec.input["file-name"]
    full_name = spec.input["download-path"]. \
        format(job=job, build=build["build"], filename=file_name)
    if not job.startswith("intel-dnv-"):
        url = "{0}/{1}".format(url, full_name)
    new_name = join(spec.environment["paths"]["DIR[WORKING,DATA]"],
                    "{job}{sep}{build}{sep}{name}".
                    format(job=job, sep=SEPARATOR, build=build["build"],
                           name=file_name))

    # Download the file from the defined source (Jenkins, logs.fd.io):
    success = _download_file(url, new_name, log)

    if success and new_name.endswith(".zip"):
        if not is_zipfile(new_name):
            success = False

    # If not successful, download from docs.fd.io:
    if not success:
        log.append(("INFO", "    Trying to download from https://docs.fd.io:"))
        release = re.search(REGEX_RELEASE, job).group(2)
        for rls in (release, "master"):
            nexus_file_name = "{job}{sep}{build}{sep}{name}". \
                format(job=job, sep=SEPARATOR, build=build["build"],
                       name=file_name)
            try:
                rls = "rls{0}".format(int(rls))
            except ValueError:
                pass
            url = "{url}/{release}/{dir}/{file}". \
                format(url=spec.environment["urls"]["URL[NEXUS]"],
                       release=rls,
                       dir=spec.environment["urls"]["DIR[NEXUS]"],
                       file=nexus_file_name)
            success = _download_file(url, new_name, log)
            if success:
                break

    if success:
        build["file-name"] = new_name
    else:
        return False

    if spec.input["file-name"].endswith(".gz"):
        if "docs.fd.io" in url:
            execute_command("gzip --decompress --keep --force {0}".
                            format(new_name))
        else:
            rename(new_name, new_name[:-3])
            execute_command("gzip --keep {0}".format(new_name[:-3]))
        build["file-name"] = new_name[:-3]

    if new_name.endswith(".zip"):
        if is_zipfile(new_name):
            return _unzip_file(spec, build, pid, log)
        else:
            log.append(("ERROR",
                        "Zip file '{0}' is corrupted.".format(new_name)))
            return False
    else:
        return True
