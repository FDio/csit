# Copyright (c) 2017 Cisco and/or its affiliates.
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

import logging

from os import rename, remove
from os.path import join, getsize
from shutil import move
from zipfile import ZipFile, is_zipfile, BadZipfile
from httplib import responses
from requests import get, codes, RequestException, Timeout, TooManyRedirects, \
    HTTPError, ConnectionError

from errors import PresentationError


# Chunk size used for file download
CHUNK_SIZE = 512

# Separator used in file names
SEPARATOR = "__"


def download_data_files(config):
    """Download all data specified in the configuration file in the section
    type: input --> builds.

    :param config: Configuration.
    :type config: Configuration
    :raises: PresentationError if there is no url defined for the job.
    """

    for job, builds in config.builds.items():
        for build in builds:
            if job.startswith("csit-"):
                url = config.environment["urls"]["URL[JENKINS,CSIT]"]
            elif job.startswith("hc2vpp-"):
                url = config.environment["urls"]["URL[JENKINS,HC]"]
            else:
                raise PresentationError("No url defined for the job '{}'.".
                                        format(job))
            file_name = config.input["file-name"]
            full_name = config.input["download-path"].\
                format(job=job, build=build["build"], filename=file_name)
            url = "{0}/{1}".format(url, full_name)
            new_name = join(
                config.environment["paths"]["DIR[WORKING,DATA]"],
                "{job}{sep}{build}{sep}{name}".format(job=job, sep=SEPARATOR,
                                                      build=build["build"],
                                                      name=file_name))

            logging.info("Downloading the file '{0}' to '{1}'.".
                         format(url, new_name))

            status = "failed"
            try:
                response = get(url, stream=True)
                code = response.status_code
                if code != codes["OK"]:
                    logging.error("{0}: {1}".format(code, responses[code]))
                    config.set_input_state(job, build["build"], "not found")
                    break

                file_handle = open(new_name, "wb")
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        file_handle.write(chunk)
                file_handle.close()

                expected_length = None
                try:
                    expected_length = int(response.headers["Content-Length"])
                    logging.debug("  Expected file size: {0}B".
                                  format(expected_length))
                except KeyError:
                    logging.debug("  No information about expected size.")

                real_length = getsize(new_name)
                logging.debug("  Downloaded size: {0}B".format(real_length))

                if expected_length:
                    if real_length == expected_length:
                        status = "downloaded"
                        logging.info("{0}: {1}".format(code, responses[code]))
                    else:
                        logging.error("The file size differs from the expected "
                                      "size.")
                else:
                    status = "downloaded"
                    logging.info("{0}: {1}".format(code, responses[code]))

            except ConnectionError as err:
                logging.error("Not possible to connect to '{0}'.".format(url))
                logging.debug(err)
            except HTTPError as err:
                logging.error("Invalid HTTP response from '{0}'.".format(url))
                logging.debug(err)
            except TooManyRedirects as err:
                logging.error("Request exceeded the configured number "
                              "of maximum re-directions.")
                logging.debug(err)
            except Timeout as err:
                logging.error("Request timed out.")
                logging.debug(err)
            except RequestException as err:
                logging.error("Unexpected HTTP request exception.")
                logging.debug(err)
            except (IOError, ValueError, KeyError) as err:
                logging.error("Download failed.")
                logging.debug("Reason: {0}".format(err))

            config.set_input_state(job, build["build"], status)
            config.set_input_file_name(job, build["build"], new_name)

            if status == "failed":
                logging.info("Removing the file '{0}'".format(new_name))
                try:
                    remove(new_name)
                except OSError as err:
                    logging.warning(str(err))
                config.set_input_file_name(job, build["build"], None)

    unzip_files(config)


def unzip_files(config):
    """Unzip downloaded zip files

    :param config: Configuration.
    :type config: Configuration
    :raises: PresentationError if the zip file does not exist or it is not a
    zip file.
    """

    if config.is_debug:
        data_file = config.debug["extract"]
    else:
        data_file = config.input["extract"]

    for job, builds in config.builds.items():
        for build in builds:
            try:
                status = "failed"
                directory = config.environment["paths"]["DIR[WORKING,DATA]"]
                file_name = join(build["file-name"])

                if build["status"] == "downloaded" and is_zipfile(file_name):
                    logging.info("Unziping: '{0}' from '{1}'.".
                                 format(data_file, file_name))
                    new_name = "{0}{1}{2}".format(file_name.rsplit('.')[-2],
                                                  SEPARATOR,
                                                  data_file.split("/")[-1])
                    try:
                        with ZipFile(file_name, 'r') as zip_file:
                            zip_file.extract(data_file, directory)
                        logging.info("Moving {0} to {1} ...".
                                     format(join(directory, data_file),
                                            directory))
                        move(join(directory, data_file), directory)
                        logging.info("Renaming the file '{0}' to '{1}'".
                                     format(join(directory,
                                                 data_file.split("/")[-1]),
                                            new_name))
                        rename(join(directory, data_file.split("/")[-1]),
                               new_name)
                        status = "unzipped"
                        config.set_input_state(job, build["build"], status)
                        config.set_input_file_name(job, build["build"],
                                                   new_name)
                    except (BadZipfile, RuntimeError) as err:
                        logging.error("Failed to unzip the file '{0}': {1}.".
                                      format(file_name, str(err)))
                    except OSError as err:
                        logging.error("Failed to rename the file '{0}': {1}.".
                                      format(data_file, str(err)))
                    finally:
                        if status == "failed":
                            config.set_input_file_name(job, build["build"],
                                                       None)
                else:
                    raise PresentationError("The file '{0}' does not exist or "
                                            "it is not a zip file".
                                            format(file_name))

                config.set_input_state(job, build["build"], status)

            except KeyError:
                pass
