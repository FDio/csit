# Copyright (c) 2019 Cisco and/or its affiliates.
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

import smtplib
import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os.path import isdir
from collections import OrderedDict

from .utils import get_last_completed_build_number
from .errors import PresentationError


class AlertingError(PresentationError):
    """Exception(s) raised by the alerting module.

    When raising this exception, put this information to the message in this
    order:
     - short description of the encountered problem (parameter msg),
     - relevant messages if there are any collected, e.g., from caught
       exception (optional parameter details),
     - relevant data if there are any collected (optional parameter details).
    """

    def __init__(self, msg, details='', level="CRITICAL"):
        """Sets the exception message and the level.

        :param msg: Short description of the encountered problem.
        :param details: Relevant messages if there are any collected, e.g.,
            from caught exception (optional parameter details), or relevant data
            if there are any collected (optional parameter details).
        :param level: Level of the error, possible choices are: "DEBUG", "INFO",
            "WARNING", "ERROR" and "CRITICAL".
        :type msg: str
        :type details: str
        :type level: str
        """

        super(AlertingError, self).__init__(
            "Alerting: {0}".format(msg), details, level)

    def __repr__(self):
        return (
            "AlertingError(msg={msg!r},details={dets!r},level={level!r})".
            format(msg=self._msg, dets=self._details, level=self._level))


class Alerting(object):
    """Class implementing the alerting mechanism.
    """

    def __init__(self, spec):
        """Initialization.

        :param spec: The CPTA specification.
        :type spec: Specification
        """

        # Implemented alerts:
        self._ALERTS = ("failed-tests", )

        self._spec = spec

        try:
            self._spec_alert = spec.alerting
        except KeyError as err:
            raise  AlertingError("Alerting is not configured, skipped.",
                                 repr(err),
                                 "WARNING")

        self._path_failed_tests = spec.environment["paths"]["DIR[STATIC,VPP]"]

        # Verify and validate input specification:
        self.configs = self._spec_alert.get("configurations", None)
        if not self.configs:
            raise AlertingError("No alert configuration is specified.")
        for config_type, config_data in self.configs.iteritems():
            if config_type == "email":
                if not config_data.get("server", None):
                    raise AlertingError("Parameter 'server' is missing.")
                if not config_data.get("address-to", None):
                    raise AlertingError("Parameter 'address-to' (recipient) is "
                                        "missing.")
                if not config_data.get("address-from", None):
                    raise AlertingError("Parameter 'address-from' (sender) is "
                                        "missing.")
            elif config_type == "jenkins":
                if not isdir(config_data.get("output-dir", "")):
                    raise AlertingError("Parameter 'output-dir' is "
                                        "missing or it is not a directory.")
                if not config_data.get("output-file", None):
                    raise AlertingError("Parameter 'output-file' is missing.")
            else:
                raise AlertingError("Alert of type '{0}' is not implemented.".
                                    format(config_type))

        self.alerts = self._spec_alert.get("alerts", None)
        if not self.alerts:
            raise AlertingError("No alert is specified.")
        for alert, alert_data in self.alerts.iteritems():
            if not alert_data.get("title", None):
                raise AlertingError("Parameter 'title' is missing.")
            if not alert_data.get("type", None) in self._ALERTS:
                raise AlertingError("Parameter 'failed-tests' is missing or "
                                    "incorrect.")
            if not alert_data.get("way", None) in self.configs.keys():
                raise AlertingError("Parameter 'way' is missing or incorrect.")
            if not alert_data.get("include", None):
                raise AlertingError("Parameter 'include' is missing or the "
                                    "list is empty.")

    def __str__(self):
        """Return string with human readable description of the alert.

        :returns: Readable description.
        :rtype: str
        """
        return "configs={configs}, alerts={alerts}".format(
            configs=self.configs, alerts=self.alerts)

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return "Alerting(spec={spec})".format(
            spec=self._spec)

    def generate_alerts(self):
        """Generate alert(s) using specified way(s).
        """

        for alert, alert_data in self.alerts.iteritems():
            if alert_data["way"] == "jenkins":
                self._generate_email_body(alert_data)
            else:
                raise AlertingError("Alert with way '{0}' is not implemented.".
                                    format(alert_data["way"]))

    @staticmethod
    def _send_email(server, addr_from, addr_to, subject, text=None, html=None):
        """Send an email using predefined configuration.

        :param server: SMTP server used to send email.
        :param addr_from: Sender address.
        :param addr_to: Recipient address(es).
        :param subject: Subject of the email.
        :param text: Message in the ASCII text format.
        :param html: Message in the HTML format.
        :type server: str
        :type addr_from: str
        :type addr_to: list
        :type subject: str
        :type text: str
        :type html: str
        """

        if not text and not html:
            raise AlertingError("No text/data to send.")

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = addr_from
        msg['To'] = ", ".join(addr_to)

        if text:
            msg.attach(MIMEText(text, 'plain'))
        if html:
            msg.attach(MIMEText(html, 'html'))

        smtp_server = None
        try:
            logging.info("Trying to send alert '{0}' ...".format(subject))
            logging.debug("SMTP Server: {0}".format(server))
            logging.debug("From: {0}".format(addr_from))
            logging.debug("To: {0}".format(", ".join(addr_to)))
            logging.debug("Message: {0}".format(msg.as_string()))
            smtp_server = smtplib.SMTP(server)
            smtp_server.sendmail(addr_from, addr_to, msg.as_string())
        except smtplib.SMTPException as err:
            raise AlertingError("Not possible to send the alert via email.",
                                str(err))
        finally:
            if smtp_server:
                smtp_server.quit()

    def _get_compressed_failed_tests(self, alert, test_set, sort=True):
        """Return the dictionary with compressed faild tests. The compression is
        done by grouping the tests from the same area but with different NICs,
        frame sizes and number of processor cores.

        For example, the failed tests:
          10ge2p1x520-64b-1c-ethip4udp-ip4scale4000-udpsrcscale15-nat44-mrr
          10ge2p1x520-64b-2c-ethip4udp-ip4scale4000-udpsrcscale15-nat44-mrr
          10ge2p1x520-64b-4c-ethip4udp-ip4scale4000-udpsrcscale15-nat44-mrr
          10ge2p1x520-imix-1c-ethip4udp-ip4scale4000-udpsrcscale15-nat44-mrr
          10ge2p1x520-imix-2c-ethip4udp-ip4scale4000-udpsrcscale15-nat44-mrr
          10ge2p1x520-imix-4c-ethip4udp-ip4scale4000-udpsrcscale15-nat44-mrr

        will be represented as:
          ethip4udp-ip4scale4000-udpsrcscale15-nat44 \
          (10ge2p1x520, 64b, imix, 1c, 2c, 4c)

        Structure of returned data:

        {
            "trimmed_TC_name_1": {
                "nics": [],
                "framesizes": [],
                "cores": []
            }
            ...
            "trimmed_TC_name_N": {
                "nics": [],
                "framesizes": [],
                "cores": []
            }
        }

        :param alert: Files are created for this alert.
        :param test_set: Specifies which set of tests will be included in the
            result. Its name is the same as the name of file with failed tests.
        :param sort: If True, the failed tests are sorted alphabetically.
        :type alert: dict
        :type test_set: str
        :type sort: bool
        :returns: CSIT build number, VPP version, Number of passed tests,
            Number of failed tests, Compressed failed tests.
        :rtype: tuple(str, str, int, int, OrderedDict)
        """

        directory = self.configs[alert["way"]]["output-dir"]
        failed_tests = OrderedDict()
        file_path = "{0}/{1}.txt".format(directory, test_set)
        version = ""
        try:
            with open(file_path, 'r') as f_txt:
                for idx, line in enumerate(f_txt):
                    if idx == 0:
                        build = line[:-1]
                        continue
                    if idx == 1:
                        version = line[:-1]
                        continue
                    if idx == 2:
                        passed = line[:-1]
                        continue
                    if idx == 3:
                        failed = line[:-1]
                        continue
                    try:
                        test = line[:-1].split('-')
                        nic = test[0]
                        framesize = test[1]
                        cores = test[2]
                        name = '-'.join(test[3:-1])
                    except IndexError:
                        continue
                    if failed_tests.get(name, None) is None:
                        failed_tests[name] = dict(nics=list(),
                                                  framesizes=list(),
                                                  cores=list())
                    if nic not in failed_tests[name]["nics"]:
                        failed_tests[name]["nics"].append(nic)
                    if framesize not in failed_tests[name]["framesizes"]:
                        failed_tests[name]["framesizes"].append(framesize)
                    if cores not in failed_tests[name]["cores"]:
                        failed_tests[name]["cores"].append(cores)
        except IOError:
            logging.error("No such file or directory: {file}".
                          format(file=file_path))
            return None, None, None, None, None
        if sort:
            sorted_failed_tests = OrderedDict()
            keys = [k for k in failed_tests.keys()]
            keys.sort()
            for key in keys:
                sorted_failed_tests[key] = failed_tests[key]
            return build, version, passed, failed, sorted_failed_tests
        else:
            return build, version, passed, failed, failed_tests

    def _generate_email_body(self, alert):
        """Create the file which is used in the generated alert.

        :param alert: Files are created for this alert.
        :type alert: dict
        """

        if alert["type"] != "failed-tests":
            raise AlertingError("Alert of type '{0}' is not implemented.".
                                format(alert["type"]))

        config = self.configs[alert["way"]]

        text = ""
        for idx, test_set in enumerate(alert.get("include", [])):
            build, version, passed, failed, failed_tests = \
                self._get_compressed_failed_tests(alert, test_set)
            if build is None:
                ret_code, build_nr, _ = get_last_completed_build_number(
                    self._spec.environment["urls"]["URL[JENKINS,CSIT]"],
                    alert["urls"][idx].split('/')[-1])
                if ret_code != 0:
                    build_nr = ''
                text += "\n\nNo input data available for '{set}'. See CSIT " \
                        "build {link}/{build} for more information.\n".\
                    format(set='-'.join(test_set.split('-')[-2:]),
                           link=alert["urls"][idx],
                           build=build_nr)
                continue
            text += ("\n\n{topo}-{arch}, "
                     "{failed} tests failed, "
                     "{passed} tests passed, "
                     "CSIT build: {link}/{build}, "
                     "VPP version: {version}\n\n".
                     format(topo=test_set.split('-')[-2],
                            arch=test_set.split('-')[-1],
                            failed=failed,
                            passed=passed,
                            link=alert["urls"][idx],
                            build=build,
                            version=version))
            regression_hdr = ("\n\n{topo}-{arch}, "
                              "CSIT build: {link}/{build}, "
                              "VPP version: {version}\n\n"
                              .format(topo=test_set.split('-')[-2],
                                      arch=test_set.split('-')[-1],
                                      link=alert["urls"][idx],
                                      build=build,
                                      version=version
                                      ))
            max_len_name = 0
            max_len_nics = 0
            max_len_framesizes = 0
            max_len_cores = 0
            for name, params in failed_tests.items():
                failed_tests[name]["nics"] = ",".join(sorted(params["nics"]))
                failed_tests[name]["framesizes"] = \
                    ",".join(sorted(params["framesizes"]))
                failed_tests[name]["cores"] = ",".join(sorted(params["cores"]))
                if len(name) > max_len_name:
                    max_len_name = len(name)
                if len(failed_tests[name]["nics"]) > max_len_nics:
                    max_len_nics = len(failed_tests[name]["nics"])
                if len(failed_tests[name]["framesizes"]) > max_len_framesizes:
                    max_len_framesizes = len(failed_tests[name]["framesizes"])
                if len(failed_tests[name]["cores"]) > max_len_cores:
                    max_len_cores = len(failed_tests[name]["cores"])

            for name, params in failed_tests.items():
                text += "{name}  {nics}  {frames}  {cores}\n".format(
                    name=name + " " * (max_len_name - len(name)),
                    nics=params["nics"] +
                        " " * (max_len_nics - len(params["nics"])),
                    frames=params["framesizes"] + " " *
                        (max_len_framesizes - len(params["framesizes"])),
                    cores=params["cores"] +
                        " " * (max_len_cores - len(params["cores"])))

            # Add list of regressions:
            file_name = "{0}/cpta-regressions-{1}.txt".\
                format(config["output-dir"], alert["urls"][idx].split('/')[-1])
            try:
                with open(file_name, 'r') as txt_file:
                    file_content = txt_file.read()
                    reg_file_name = "{dir}/trending-regressions.txt". \
                        format(dir=config["output-dir"])
                    with open(reg_file_name, 'a+') as reg_file:
                        reg_file.write(regression_hdr)
                        if file_content:
                            reg_file.write(file_content)
                        else:
                            reg_file.write("No regressions")
            except IOError as err:
                logging.warning(repr(err))

            # Add list of progressions:
            file_name = "{0}/cpta-progressions-{1}.txt".\
                format(config["output-dir"], alert["urls"][idx].split('/')[-1])
            try:
                with open(file_name, 'r') as txt_file:
                    file_content = txt_file.read()
                    pro_file_name = "{dir}/trending-progressions.txt". \
                        format(dir=config["output-dir"])
                    with open(pro_file_name, 'a+') as pro_file:
                        pro_file.write(regression_hdr)
                        if file_content:
                            pro_file.write(file_content)
                        else:
                            pro_file.write("No progressions")
            except IOError as err:
                logging.warning(repr(err))

        text += "\nFor detailed information visit: {url}\n".\
            format(url=alert["url-details"])
        file_name = "{0}/{1}".format(config["output-dir"],
                                     config["output-file"])
        logging.info("Writing the file '{0}.txt' ...".format(file_name))

        try:
            with open("{0}.txt".format(file_name), 'w') as txt_file:
                txt_file.write(text)
        except IOError:
            logging.error("Not possible to write the file '{0}.txt'.".
                          format(file_name))
