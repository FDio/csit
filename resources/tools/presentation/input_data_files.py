# Copyright (c) 2020 Cisco and/or its affiliates.
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
import gzip

from os import rename, mkdir
from os.path import join
from http.client import responses
from zipfile import ZipFile, is_zipfile, BadZipfile

import requests

from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import RequestException
from requests import codes

from pal_errors import PresentationError


# Chunk size used for file download
CHUNK_SIZE = 512

# Separator used in file names
SEPARATOR = u"__"

REGEX_RELEASE = re.compile(r'(\D*)(\d{4}|master)(\D*)')


def _download_file(url, file_name, arch=False):
    """Download a file with input data.

    :param url: URL to the file to download.
    :param file_name: Name of file to download.
    :param arch: If True, also .gz file is downloaded
    :type url: str
    :type file_name: str
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
        session.mount(u"http://", adapter)
        session.mount(u"https://", adapter)
        return session

    success = False
    session = None
    try:
        logging.info(f"    Connecting to {url} ...")
        session = requests_retry_session()
        response = session.get(url, stream=True, verify=False)
        code = response.status_code
        logging.info(f"    {code}: {responses[code]}")

        if code != codes[u"OK"]:
            if session:
                session.close()
            url = url.replace(u"_info", u"")
            logging.info(f"    Connecting to {url} ...")
            session = requests_retry_session()
            response = session.get(url, stream=True, verify=False)
            code = response.status_code
            logging.info(f"    {code}: {responses[code]}")
            if code != codes[u"OK"]:
                return False, file_name
            file_name = file_name.replace(u"_info", u"")

        dst_file_name = file_name.replace(u".gz", u"")
        logging.info(f"    Downloading the file {url} to {dst_file_name} ...")
        with open(dst_file_name, u"wb") as file_handle:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file_handle.write(chunk)

        if arch and u".gz" in file_name:
            if session:
                session.close()
            logging.info(f"    Downloading the file {url} to {file_name} ...")
            session = requests_retry_session()
            response = session.get(url, stream=True, verify=False)
            if response.status_code == codes[u"OK"]:
                with open(file_name, u"wb") as file_handle:
                    file_handle.write(response.raw.read())
            else:
                logging.error(
                    f"Not possible to download the file {url} to {file_name}"
                )

        success = True
    except RequestException as err:
        logging.error(f"HTTP Request exception:\n{repr(err)}")
    except (IOError, ValueError, KeyError) as err:
        logging.error(f"Download failed.\n{repr(err)}")
    finally:
        if session:
            session.close()

    logging.info(u"    Download finished.")
    return success, file_name


def _unzip_file(spec, build, pid):
    """Unzip downloaded source file.

    :param spec: Specification read form the specification file.
    :param build: Information about the build.
    :type spec: Specification
    :type build: dict
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    file_name = build[u"file-name"]
    if u".zip" in file_name:
        data_file = spec.input[u"zip-extract"]
    else:
        data_file = spec.input[u"extract"]

    directory = spec.environment[u"paths"][u"DIR[WORKING,DATA]"]
    tmp_dir = join(directory, str(pid))
    try:
        mkdir(tmp_dir)
    except OSError:
        pass
    new_name = \
        f"{file_name.rsplit(u'.')[-2]}{SEPARATOR}{data_file.split(u'/')[-1]}"

    logging.info(f"    Unzipping: {data_file} from {file_name}.")
    try:
        with ZipFile(file_name, u'r') as zip_file:
            zip_file.extract(data_file, tmp_dir)
        logging.info(
            f"    Renaming the file {join(tmp_dir, data_file)} to {new_name}"
        )
        rename(join(tmp_dir, data_file), new_name)
        build[u"file-name"] = new_name
        return True
    except (BadZipfile, RuntimeError) as err:
        logging.error(f"Failed to unzip the file {file_name}: {repr(err)}.")
        return False
    except OSError as err:
        logging.error(f"Failed to rename the file {data_file}: {repr(err)}.")
        return False


def download_and_unzip_data_file(spec, job, build, pid):
    """Download and unzip a source file.

    :param spec: Specification read form the specification file.
    :param job: Name of the Jenkins job.
    :param build: Information about the build.
    :param pid: PID of the process executing this method.
    :type spec: Specification
    :type job: str
    :type build: dict
    :type pid: int
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    # Try to download .gz from s3_storage
    file_name = spec.input[u"file-name"]
    url = u"{0}/{1}".format(
        spec.environment[u'urls'][u'URL[S3_STORAGE,LOG]'],
        spec.input[u'download-path'].format(
            job=job, build=build[u'build'], filename=file_name
        )
    )
    new_name = join(
        spec.environment[u"paths"][u"DIR[WORKING,DATA]"],
        f"{job}{SEPARATOR}{build[u'build']}{SEPARATOR}{file_name}"
    )

    logging.info(f"Trying to download {url}")

    arch = bool(spec.configuration.get(u"archive-inputs", True))
    success, downloaded_name = _download_file(url, new_name, arch=arch)

    if not success:
        # Try to download .gz from logs.fd.io
        file_name = spec.input[u"file-name"]
        url = u"{0}/{1}".format(
            spec.environment[u'urls'][u'URL[NEXUS,LOG]'],
            spec.input[u'download-path'].format(
                job=job, build=build[u'build'], filename=file_name
            )
        )
        new_name = join(
            spec.environment[u"paths"][u"DIR[WORKING,DATA]"],
            f"{job}{SEPARATOR}{build[u'build']}{SEPARATOR}{file_name}"
        )

        logging.info(f"Trying to download {url}")

        arch = bool(spec.configuration.get(u"archive-inputs", True))
        success, downloaded_name = _download_file(url, new_name, arch=arch)

    if not success:

        # Try to download .gz or .zip from docs.fd.io
        file_name = (spec.input[u"file-name"], spec.input[u"zip-file-name"])
        release = re.search(REGEX_RELEASE, job).group(2)
        for idx, rls in enumerate((release, u"master", )):
            try:
                rls = f"rls{int(rls)}"
            except ValueError:
                # It is master
                pass
            url = (
                f"{spec.environment[u'urls'][u'URL[NEXUS,DOC]']}/"
                f"{rls}/"
                f"{spec.environment[u'urls'][u'DIR[NEXUS,DOC]']}/"
                f"{job}{SEPARATOR}{build[u'build']}{SEPARATOR}{file_name[idx]}"
            )

            logging.info(f"Downloading {url}")

            new_name = join(
                spec.environment[u"paths"][u"DIR[WORKING,DATA]"],
                f"{job}{SEPARATOR}{build[u'build']}{SEPARATOR}{file_name[idx]}"
            )
            success, downloaded_name = _download_file(url, new_name, arch=arch)
            if success:
                file_name = file_name[idx]
                if file_name.endswith(u".gz"):
                    with gzip.open(downloaded_name[:-3], u"rb") as gzip_file:
                        file_content = gzip_file.read()
                    with open(downloaded_name[:-3], u"wb") as xml_file:
                        xml_file.write(file_content)
                break

    if not success:

        # Try to download .zip from jenkins.fd.io
        file_name = spec.input[u"zip-file-name"]
        download_path = spec.input[u"zip-download-path"]
        if job.startswith(u"csit-"):
            url = spec.environment[u"urls"][u"URL[JENKINS,CSIT]"]
        else:
            raise PresentationError(f"No url defined for the job {job}.")

        full_name = download_path.format(
            job=job, build=build[u"build"], filename=file_name
        )
        url = u"{0}/{1}".format(url, full_name)
        new_name = join(
            spec.environment[u"paths"][u"DIR[WORKING,DATA]"],
            f"{job}{SEPARATOR}{build[u'build']}{SEPARATOR}{file_name}"
        )

        logging.info(f"Downloading {url}")

        success, downloaded_name = _download_file(url, new_name)

    if success and downloaded_name.endswith(u".zip"):
        if not is_zipfile(downloaded_name):
            logging.error(f"Zip file {new_name} is corrupted.")
            success = False

    if success:
        build[u"file-name"] = downloaded_name

        if file_name.endswith(u".gz"):
            build[u"file-name"] = downloaded_name[:-3]

        if downloaded_name.endswith(u".zip"):
            success = _unzip_file(spec, build, pid)

    return success
