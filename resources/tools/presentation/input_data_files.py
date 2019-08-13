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
import requests
import logging

from os import rename, mkdir
from os.path import join
from zipfile import ZipFile, is_zipfile, BadZipfile
from httplib import responses
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests import codes, RequestException, Timeout, TooManyRedirects, \
    HTTPError, ConnectionError

from errors import PresentationError


# Chunk size used for file download
CHUNK_SIZE = 512

# Separator used in file names
SEPARATOR = "__"

REGEX_RELEASE = re.compile(r'(\D*)(\d{4}|master)(\D*)')


def _download_file(url, file_name, log, arch=False):
    """Download a file with input data.

    :param url: URL to the file to download.
    :param file_name: Name of file to download.
    :param log: List of log messages.
    :param arch: If True, also .gz file is downloaded
    :type url: str
    :type file_name: str
    :type log: list of tuples (severity, msg)
    :type arch: bool
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    def requests_retry_session(retries=3,
                               backoff_factor=0.3,
                               status_forcelist=(500, 502, 504)):
        """

        :param retries: Total number of retries to allow.
        :param backoff_factor: A backoff factor to apply between attempts after
            the second try.
        :param status_forcelist: A set of integer HTTP status codes that are
            forced to retry.
        :type retries: int
        :type backoff_factor: float
        :type status_forcelist: iterable
        :returns: Session object.
        :rtype: requests.Session
        """

        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    success = False
    try:
        log.append(("INFO", "    Connecting to '{0}' ...".format(url)))
        response = requests_retry_session().get(url, stream=True)
        code = response.status_code
        log.append(("INFO", "    {0}: {1}".format(code, responses[code])))

        if code != codes["OK"]:
            url = url.replace("_info", "")
            log.append(("INFO", "    Connecting to '{0}' ...".format(url)))
            response = requests_retry_session().get(url, stream=True)
            code = response.status_code
            log.append(("INFO", "    {0}: {1}".format(code, responses[code])))
            if code != codes["OK"]:
                return False, file_name
            file_name = file_name.replace("_info", "")

        log.append(("INFO", "    Downloading the file '{0}' to '{1}' ...".
                    format(url, file_name)))

        dst_file_name = file_name.replace(".gz", "")
        with open(dst_file_name, "wb") as file_handle:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file_handle.write(chunk)

        if arch and ".gz" in file_name:
            with open(file_name, "wb") as file_handle:
                file_handle.write(response.raw.read())

        success = True
    except ConnectionError as err:
        log.append(("ERROR", "Not possible to connect to '{0}'.".format(url)))
        log.append(("DEBUG", repr(err)))
    except HTTPError as err:
        log.append(("ERROR", "Invalid HTTP response from '{0}'.".format(url)))
        log.append(("DEBUG", repr(err)))
    except TooManyRedirects as err:
        log.append(("ERROR", "Request exceeded the configured number "
                             "of maximum re-directions."))
        log.append(("DEBUG", repr(err)))
    except Timeout as err:
        log.append(("ERROR", "Request timed out."))
        log.append(("DEBUG", repr(err)))
    except RequestException as err:
        log.append(("ERROR", "Unexpected HTTP request exception."))
        log.append(("DEBUG", repr(err)))
    except (IOError, ValueError, KeyError) as err:
        log.append(("ERROR", "Download failed."))
        log.append(("DEBUG", repr(err)))

    log.append(("INFO", "    Download finished."))
    return success, file_name


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

    file_name = build["file-name"]
    if ".zip" in file_name:
        data_file = spec.input["zip-extract"]
    else:
        data_file = spec.input["extract"]

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

    # Try to download .gz from logs.fd.io

    file_name = spec.input["file-name"]
    url = "{0}/{1}".format(
        spec.environment["urls"]["URL[NEXUS,LOG]"],
        spec.input["download-path"].format(
            job=job, build=build["build"], filename=file_name))
    new_name = join(spec.environment["paths"]["DIR[WORKING,DATA]"],
                    "{job}{sep}{build}{sep}{name}".format(
                        job=job, sep=SEPARATOR, build=build["build"],
                        name=file_name))

    logging.info("Downloading {0}".format(url))

    arch = True if spec.configuration.get("archive-inputs", True) else False
    success, downloaded_name = _download_file(url, new_name, log, arch=arch)

    if not success:

        # Try to download .gz from docs.fd.io

        file_name = spec.input["file-name"]
        url = "{0}/{1}".format(
            spec.environment["urls"]["URL[NEXUS,DOC]"],
            spec.input["download-path"].format(
                job=job, build=build["build"], filename=file_name))
        new_name = join(spec.environment["paths"]["DIR[WORKING,DATA]"],
                        "{job}{sep}{build}{sep}{name}".format(
                            job=job, sep=SEPARATOR, build=build["build"],
                            name=file_name))

        logging.info("Downloading {0}".format(url))

        if spec.configuration.get("archive-inputs", True):
            arch = True
        success, downloaded_name = _download_file(url, new_name, log, arch=arch)

    if not success:

        # Try to download .zip from docs.fd.io

        file_name = spec.input["zip-file-name"]
        new_name = join(spec.environment["paths"]["DIR[WORKING,DATA]"],
                        "{job}{sep}{build}{sep}{name}".format(
                            job=job, sep=SEPARATOR, build=build["build"],
                            name=file_name))
        release = re.search(REGEX_RELEASE, job).group(2)
        for rls in (release, "master"):
            nexus_file_name = "{job}{sep}{build}{sep}{name}". \
                format(job=job, sep=SEPARATOR, build=build["build"],
                       name=file_name)
            try:
                rls = "rls{0}".format(int(rls))
            except ValueError:
                # It is 'master'
                pass
            url = "{url}/{release}/{dir}/{file}". \
                format(url=spec.environment["urls"]["URL[NEXUS,DOC]"],
                       release=rls,
                       dir=spec.environment["urls"]["DIR[NEXUS,DOC]"],
                       file=nexus_file_name)

            logging.info("Downloading {0}".format(url))

            success, downloaded_name = _download_file(url, new_name, log)
            if success:
                break

    if not success:

        # Try to download .zip from jenkins.fd.io

        file_name = spec.input["zip-file-name"]
        download_path = spec.input["zip-download-path"]
        if job.startswith("csit-"):
            url = spec.environment["urls"]["URL[JENKINS,CSIT]"]
        elif job.startswith("hc2vpp-"):
            url = spec.environment["urls"]["URL[JENKINS,HC]"]
        else:
            raise PresentationError(
                "No url defined for the job '{}'.".format(job))

        full_name = download_path.format(
            job=job, build=build["build"], filename=file_name)
        url = "{0}/{1}".format(url, full_name)
        new_name = join(spec.environment["paths"]["DIR[WORKING,DATA]"],
                        "{job}{sep}{build}{sep}{name}".
                        format(job=job, sep=SEPARATOR, build=build["build"],
                               name=file_name))

        logging.info("Downloading {0}".format(url))

        success, downloaded_name = _download_file(url, new_name, log)

    if success and downloaded_name.endswith(".zip"):
        if not is_zipfile(downloaded_name):
            log.append(("ERROR",
                        "Zip file '{0}' is corrupted.".format(new_name)))
            success = False

    if success:
        build["file-name"] = downloaded_name

        if file_name.endswith(".gz"):
            build["file-name"] = downloaded_name[:-3]

        if downloaded_name.endswith(".zip"):
            success = _unzip_file(spec, build, pid, log)

    return success
