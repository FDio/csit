# Copyright (c) 2021 Cisco and/or its affiliates.
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

from os import rename, mkdir, makedirs, error
from os.path import join
from shutil import rmtree
from http.client import responses, HTTPException
from zipfile import ZipFile, is_zipfile, BadZipfile
from json import dump

import requests
import botocore

from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import RequestException
from requests import codes

from urllib3.exceptions import HTTPError

from resources.tools.storage import Storage

# Chunk size used for file download
CHUNK_SIZE = 512

# Separator used in file names
SEPARATOR = u"__"

REGEX_RELEASE = re.compile(r'(\D*)(\d{4}|master)(\D*)')


def _download_file(url, file_name, arch=False, verify=True, repeat=1):
    """Download a file with input data.

    :param url: URL to the file to download.
    :param file_name: Name of file to download.
    :param arch: If True, also .gz file is downloaded.
    :param verify: If true, verify the certificate.
    :param repeat: The number of attempts to download the file.
    :type url: str
    :type file_name: str
    :type arch: bool
    :type verify: bool
    :type repeat: int
    :returns: True if the download was successful, otherwise False.
    :rtype: bool
    """

    def requests_retry_session(retries=3,
                               backoff_factor=0.3,
                               status_forcelist=(500, 502, 504)):
        """Create a session with retry capabilities.

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
    while repeat:
        repeat -= 1
        session = None
        try:
            logging.info(f"  Connecting to {url} ...")
            session = requests_retry_session()
            response = session.get(url, stream=True, verify=verify)
            code = response.status_code
            logging.info(f"  {code}: {responses[code]}")

            if code != codes[u"OK"]:
                if session:
                    session.close()
                return False, file_name

            dst_file_name = file_name.replace(u".gz", u"")
            logging.info(f"  Downloading the file {url} to {dst_file_name}")
            with open(dst_file_name, u"wb") as file_handle:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        file_handle.write(chunk)

            if arch and u".gz" in file_name:
                if session:
                    session.close()
                logging.info(f"  Downloading the file {url} to {file_name}")
                session = requests_retry_session()
                response = session.get(url, stream=True, verify=verify)
                if response.status_code == codes[u"OK"]:
                    with open(file_name, u"wb") as file_handle:
                        file_handle.write(response.raw.read())
                else:
                    logging.error(
                        f"Not possible to download the file "
                        f"{url} to {file_name}"
                    )

            success = True
            repeat = 0
        except (HTTPException, HTTPError) as err:
            logging.error(f"Connection broken:\n{repr(err)}")
        except RequestException as err:
            logging.error(f"HTTP Request exception:\n{repr(err)}")
        except (IOError, ValueError, KeyError) as err:
            logging.error(f"Download failed.\n{repr(err)}")
        finally:
            if session:
                session.close()
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
    data_file = "robot-plugin/output.xml"
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


def _download_json(source, job, build, w_dir, arch):
    """Download a set of json files for specified job and build.

    :param source: The source specified in the specification file.
    :param job: The job from which the data will be downloaded.
    :param build:  The build from which the data will be downloaded.
    :param w_dir: Path to working directory
    :param arch: If true, archive the downloaded files. Not supported.
    :type source: dict
    :type job: str
    :type build: dict
    :type w_dir: str
    :type arch: bool
    :returns: Tuple (successful download: true | false, path to directory
        with json files).
    :rtype: tuple(bool, str)
    """

    _ = arch  # No archiving supported.
    json_dir = join(w_dir, u"json")

    logging.info(f"  Trying to download from {source.get(u'url', u'')}")

    # Check the information about the source
    if not source.get(u"url", None):
        logging.error(u"Missing the parameter 'url' in source specification.")
        return False, json_dir
    if not source.get(u"profile-name", None):
        logging.error(
            u"Missing the parameter 'profile-name' in source specification."
        )
        return False, json_dir
    if not source.get(u"bucket", None):
        logging.error(
            u"Missing the parameter 'bucket' in source specification."
        )
        return False, json_dir
    if not source.get(u"file-format", None):
        logging.error(
            u"Missing the parameter 'file-format' in source specification."
        )
        return False, json_dir

    try:
        # Clean:
        rmtree(json_dir)
    except FileNotFoundError:
        pass  # It does not exist
    try:
        # Make brand new empty directory for downloaded json files.
        makedirs(json_dir)
    except error as err:
        logging.error(f"Cannot create the directory {json_dir}\n{err!r}")
        return False, json_dir

    try:
        json_iterator = Storage(
            endpoint_url=source[u"url"],
            bucket=source[u"bucket"],
            profile_name=source[u"profile-name"]
        ).s3_dump_file_processing(
            prefix=join(job, str(build[u'build'])),
            suffix=source[u"file-format"]
        )
    except ValueError as err:
        logging.error(
            f"The specified url {source[u'url']} does not exist\n{err!r}"
        )
        return False, json_dir
    except botocore.exceptions.ProfileNotFound as err:
        logging.error(f"botocore: {err!r}")
        return False, json_dir
    except botocore.exceptions.ConnectTimeoutError as err:
        logging.error(f"{err!r}")
        return False, json_dir

    try:
        length = 0
        for item in json_iterator:
            file_path = join(json_dir, u".".join(item[0].split(u"/")[2:]))[:-3]
            try:
                with open(file_path, u"w") as file_handler:
                    dump(item[1], file_handler)
                length += len(str(item[1]))
            except OSError as err:
                logging.warning(f"{err!r}")
                return False, json_dir
    except botocore.exceptions.ClientError as err:
        logging.error(f"{err!r}")
        return False, json_dir
    except botocore.exceptions.ConnectTimeoutError as err:
        logging.error(f"{err!r}")
        return False, json_dir

    return bool(length), json_dir


def _download_xml(source, job, build, w_dir, arch):
    """Download an xml file for specified job and build.

    :param source: The source specified in the specification file.
    :param job: The job from which the data will be downloaded.
    :param build:  The build from which the data will be downloaded.
    :param w_dir: Path to working directory
    :param arch: If true, archive the downloaded files.
    :type source: dict
    :type job: str
    :type build: dict
    :type w_dir: str
    :type arch: bool
    :returns: Tuple (successful download: true | false, path to xml file).
    :rtype: tuple(bool, str)
    """

    file_name = source.get(u"file-name", u"")
    new_name = join(
        w_dir,
        f"{job}{SEPARATOR}{build[u'build']}{SEPARATOR}{file_name}"
    )
    url = u"{0}/{1}".format(
        source.get(u"url", u""),
        source.get(u"path", u"").format(
            job=job, build=build[u'build'], filename=file_name
        )
    )
    logging.info(f"  Trying to download {url}")
    success, downloaded_name = _download_file(
        url, new_name, arch=arch, verify=(u"nginx" not in url), repeat=3
    )
    return success, downloaded_name


def _download_xml_docs(source, job, build, w_dir, arch):
    """Download an xml file for specified job and build from docs.fd.io

    :param source: The source specified in the specification file.
    :param job: The job from which the data will be downloaded.
    :param build:  The build from which the data will be downloaded.
    :param w_dir: Path to working directory
    :param arch: If true, archive the downloaded files.
    :type source: dict
    :type job: str
    :type build: dict
    :type w_dir: str
    :type arch: bool
    :returns: Tuple (successful download: true | false, path to xml file).
    :rtype: tuple(bool, str)
    """

    file_name = source.get(u"file-name", u"")
    release = re.search(REGEX_RELEASE, job).group(2)
    for rls in (release, u"master"):
        try:
            rls = f"rls{int(rls)}"
        except ValueError:
            pass  # It is master
        url = (
            f"{source.get(u'url', u'')}/"
            f"{rls}/"
            f"{source.get(u'path', u'')}/"
            f"{job}{SEPARATOR}{build[u'build']}{SEPARATOR}{file_name}"
        )
        new_name = join(
            w_dir,
            f"{job}{SEPARATOR}{build[u'build']}{SEPARATOR}{file_name}"
        )

        logging.info(f"  Trying to download {url}")

        success, downloaded_name = _download_file(url, new_name, arch=arch)
        if success:
            if file_name.endswith(u".gz"):
                with gzip.open(downloaded_name[:-3], u"rb") as gzip_file:
                    file_content = gzip_file.read()
                with open(downloaded_name[:-3], u"wb") as xml_file:
                    xml_file.write(file_content)
            break

    return success, downloaded_name


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

    download = {
        "xml": _download_xml,
        "xml-docs": _download_xml_docs
    }

    success = False
    downloaded_name = u""
    arch = bool(spec.environment.get(u"archive-inputs", True))

    for source in spec.environment.get(u"data-sources", tuple()):
        if not source.get(u"enabled", False):
            continue
        download_type = source.get(u"type", None)
        if not download_type:
            continue
        success, downloaded_name = download[download_type](
            source,
            job,
            build,
            spec.environment[u"paths"][u"DIR[WORKING,DATA]"],
            arch
        )
        if success:
            source[u"successful-downloads"] += 1
            build[u"source"] = source[u"type"]
            break

    # TODO: Remove when only .gz is used.
    if success and downloaded_name.endswith(u".zip"):
        if not is_zipfile(downloaded_name):
            logging.error(f"Zip file {downloaded_name} is corrupted.")
            success = False

    if success:
        if downloaded_name.endswith(u".gz"):
            build[u"file-name"] = downloaded_name[:-3]
        # TODO: Remove when only .gz is used.
        elif downloaded_name.endswith(u".zip"):
            build[u"file-name"] = downloaded_name
            success = _unzip_file(spec, build, pid)
        else:
            build[u"file-name"] = downloaded_name

    return success
