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


import os
import logging
from httplib import responses
from requests import get, codes, RequestException, Timeout, TooManyRedirects, \
    HTTPError, ConnectionError

from errors import PresentationError


CHUNK_SIZE = 512


def download_data_files(config):
    """Download all data specified in the configuration file in the section
    type: input --> builds.

    :param config: Configuration.
    :type config: Configuration
    :raises: PresentationError if there is no url defined for the job.
    """
    file_name = config.input["file-name"]

    for job, builds in config.builds.items():
        for build in builds:
            if job.startswith("csit-"):
                url = config.environment["urls"]["URL[JENKINS,CSIT]"]
            elif job.startswith("hc2vpp-"):
                url = config.environment["urls"]["URL[JENKINS,HC]"]
            else:
                raise PresentationError("No url defined for the job '{}'.".
                                        format(job))
            url = "{}/{}/{}/robot/report/{}".format(url, job, build["build"],
                                                    file_name)
            new_name = os.path.join(
                config.environment["paths"]["DIR[WORKING,DATA]"],
                "{}-{}.xml".format(job, build["build"]))

            logging.info("Downloading the file '{}' to '{}'.".
                         format(url, new_name))

            status = "failed"
            try:
                response = get(url, stream=True)
                code = response.status_code
                if code != codes["OK"]:
                    logging.error("{}: {}".format(code, responses[code]))
                    config.set_input_state(job, build["build"], "not found")
                    break

                file_handle = open(new_name, "wb")
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        file_handle.write(chunk)
                file_handle.close()

                expected_length = int(response.headers["Content-Length"])
                logging.debug("  Expected file size: {}B".
                              format(expected_length))
                real_length = os.path.getsize(new_name)
                logging.debug("  Downloaded size: {}B".format(real_length))

                if real_length == expected_length:
                    status = "downloaded"
                    logging.info("{}: {}".format(code, responses[code]))
                else:
                    logging.error("The file size differs from the expected "
                                  "size.")
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
                logging.debug(err)

            config.set_input_state(job, build["build"], status)
