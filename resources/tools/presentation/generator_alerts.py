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

"""Generator of alerts:
- failed tests
- regressions
- progressions
"""


import smtplib
import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os.path import isdir
from collections import OrderedDict

from pal_utils import get_last_completed_build_number
from pal_errors import PresentationError


class AlertingError(PresentationError):
    """Exception(s) raised by the alerting module.

    When raising this exception, put this information to the message in this
    order:
     - short description of the encountered problem (parameter msg),
     - relevant messages if there are any collected, e.g., from caught
       exception (optional parameter details),
     - relevant data if there are any collected (optional parameter details).
    """

    def __init__(self, msg, details=u'', level=u"CRITICAL"):
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

        super(AlertingError, self).__init__(f"Alerting: {msg}", details, level)

    def __repr__(self):
        return (
            f"AlertingError(msg={self._msg!r},details={self._details!r},"
            f"level={self._level!r})"
        )


class Alerting:
    """Class implementing the alerting mechanism.
    """

    def __init__(self, spec):
        """Initialization.

        :param spec: The CPTA specification.
        :type spec: Specification
        """

        # Implemented alerts:
        self._implemented_alerts = (u"failed-tests", )

        self._spec = spec

        try:
            self._spec_alert = spec.alerting
        except KeyError as err:
            raise AlertingError(u"Alerting is not configured, skipped.",
                                repr(err),
                                u"WARNING")

        self._path_failed_tests = spec.environment[u"paths"][u"DIR[STATIC,VPP]"]

        # Verify and validate input specification:
        self.configs = self._spec_alert.get(u"configurations", None)
        if not self.configs:
            raise AlertingError(u"No alert configuration is specified.")
        for config_type, config_data in self.configs.items():
            if config_type == u"email":
                if not config_data.get(u"server", None):
                    raise AlertingError(u"Parameter 'server' is missing.")
                if not config_data.get(u"address-to", None):
                    raise AlertingError(u"Parameter 'address-to' (recipient) "
                                        u"is missing.")
                if not config_data.get(u"address-from", None):
                    raise AlertingError(u"Parameter 'address-from' (sender) is "
                                        u"missing.")
            elif config_type == u"jenkins":
                if not isdir(config_data.get(u"output-dir", u"")):
                    raise AlertingError(u"Parameter 'output-dir' is "
                                        u"missing or it is not a directory.")
                if not config_data.get(u"output-file", None):
                    raise AlertingError(u"Parameter 'output-file' is missing.")
            else:
                raise AlertingError(
                    f"Alert of type {config_type} is not implemented."
                )

        self.alerts = self._spec_alert.get(u"alerts", None)
        if not self.alerts:
            raise AlertingError(u"No alert is specified.")
        for alert_data in self.alerts.values():
            if not alert_data.get(u"title", None):
                raise AlertingError(u"Parameter 'title' is missing.")
            if not alert_data.get(u"type", None) in self._implemented_alerts:
                raise AlertingError(u"Parameter 'failed-tests' is missing or "
                                    u"incorrect.")
            if not alert_data.get(u"way", None) in self.configs.keys():
                raise AlertingError(u"Parameter 'way' is missing or incorrect.")
            if not alert_data.get(u"include", None):
                raise AlertingError(u"Parameter 'include' is missing or the "
                                    u"list is empty.")

    def __str__(self):
        """Return string with human readable description of the alert.

        :returns: Readable description.
        :rtype: str
        """
        return f"configs={self.configs}, alerts={self.alerts}"

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return f"Alerting(spec={self._spec})"

    def generate_alerts(self):
        """Generate alert(s) using specified way(s).
        """

        for alert_data in self.alerts.values():
            if alert_data[u"way"] == u"jenkins":
                self._generate_email_body(alert_data)
            else:
                raise AlertingError(
                    f"Alert with way {alert_data[u'way']} is not implemented."
                )

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
            raise AlertingError(u"No text/data to send.")

        msg = MIMEMultipart(u'alternative')
        msg[u'Subject'] = subject
        msg[u'From'] = addr_from
        msg[u'To'] = u", ".join(addr_to)

        if text:
            msg.attach(MIMEText(text, u'plain'))
        if html:
            msg.attach(MIMEText(html, u'html'))

        smtp_server = None
        try:
            logging.info(f"Trying to send alert {subject} ...")
            logging.debug(f"SMTP Server: {server}")
            logging.debug(f"From: {addr_from}")
            logging.debug(f"To: {u', '.join(addr_to)}")
            logging.debug(f"Message: {msg.as_string()}")
            smtp_server = smtplib.SMTP(server)
            smtp_server.sendmail(addr_from, addr_to, msg.as_string())
        except smtplib.SMTPException as err:
            raise AlertingError(u"Not possible to send the alert via email.",
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

        directory = self.configs[alert[u"way"]][u"output-dir"]
        failed_tests = OrderedDict()
        file_path = f"{directory}/{test_set}.txt"
        version = u""
        try:
            with open(file_path, u'r') as f_txt:
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
                        test = line[:-1].split(u'-')
                        name = u'-'.join(test[3:-1])
                    except IndexError:
                        continue
                    if failed_tests.get(name, None) is None:
                        failed_tests[name] = dict(nics=list(),
                                                  framesizes=list(),
                                                  cores=list())
                    if test[0] not in failed_tests[name][u"nics"]:
                        failed_tests[name][u"nics"].append(test[0])
                    if test[1] not in failed_tests[name][u"framesizes"]:
                        failed_tests[name][u"framesizes"].append(test[1])
                    if test[2] not in failed_tests[name][u"cores"]:
                        failed_tests[name][u"cores"].append(test[2])
        except IOError:
            logging.error(f"No such file or directory: {file_path}")
            return None, None, None, None, None
        if sort:
            sorted_failed_tests = OrderedDict()
            for key in sorted(failed_tests.keys()):
                sorted_failed_tests[key] = failed_tests[key]
            return build, version, passed, failed, sorted_failed_tests

        return build, version, passed, failed, failed_tests

    def _list_gressions(self, alert, idx, header, re_pro):
        """Create a file with regressions or progressions for the test set
        specified by idx.

        :param alert: Files are created for this alert.
        :param idx: Index of the test set as it is specified in the
            specification file.
        :param header: The header of the list of [re|pro]gressions.
        :param re_pro: 'regression' or 'progression'.
        :type alert: dict
        :type idx: int
        :type header: str
        :type re_pro: str
        """

        if re_pro not in (u"regressions", u"progressions"):
            return

        in_file = (
            f"{self.configs[alert[u'way']][u'output-dir']}/"
            f"{re_pro}-{alert[u'urls'][idx].split(u'/')[-1]}.txt"
        )
        out_file = (
            f"{self.configs[alert[u'way']][u'output-dir']}/"
            f"trending-{re_pro}.txt"
        )

        try:
            with open(in_file, u'r') as txt_file:
                file_content = txt_file.read()
                with open(out_file, u'a+') as reg_file:
                    reg_file.write(header)
                    if file_content:
                        reg_file.write(file_content)
                    else:
                        reg_file.write(f"No {re_pro}")
        except IOError as err:
            logging.warning(repr(err))

    def _generate_email_body(self, alert):
        """Create the file which is used in the generated alert.

        :param alert: Files are created for this alert.
        :type alert: dict
        """

        if alert[u"type"] != u"failed-tests":
            raise AlertingError(
                f"Alert of type {alert[u'type']} is not implemented."
            )

        text = u""
        for idx, test_set in enumerate(alert.get(u"include", [])):
            build, version, passed, failed, failed_tests = \
                self._get_compressed_failed_tests(alert, test_set)
            if build is None:
                ret_code, build_nr, _ = get_last_completed_build_number(
                    self._spec.environment[u"urls"][u"URL[JENKINS,CSIT]"],
                    alert[u"urls"][idx].split(u'/')[-1])
                if ret_code != 0:
                    build_nr = u''
                text += (
                    f"\n\nNo input data available for "
                    f"{u'-'.join(test_set.split('-')[-2:])}. See CSIT build "
                    f"{alert[u'urls'][idx]}/{build_nr} for more information.\n"
                )
                continue
            text += (
                f"\n\n{test_set.split('-')[-2]}-{test_set.split('-')[-1]}, "
                f"{failed} tests failed, "
                f"{passed} tests passed, CSIT build: "
                f"{alert[u'urls'][idx]}/{build}, VPP version: {version}\n\n"
            )

            class MaxLens():
                """Class to store the max lengths of strings displayed in
                failed tests list.
                """
                def __init__(self, tst_name, nics, framesizes, cores):
                    """Initialisation.

                    :param tst_name: Name of the test.
                    :param nics: NICs used in the test.
                    :param framesizes: Frame sizes used in the tests
                    :param cores: Cores used in th test.
                    """
                    self.name = tst_name
                    self.nics = nics
                    self.frmsizes = framesizes
                    self.cores = cores

            max_len = MaxLens(0, 0, 0, 0)

            for name, params in failed_tests.items():
                failed_tests[name][u"nics"] = u",".join(sorted(params[u"nics"]))
                failed_tests[name][u"framesizes"] = \
                    u",".join(sorted(params[u"framesizes"]))
                failed_tests[name][u"cores"] = \
                    u",".join(sorted(params[u"cores"]))
                if len(name) > max_len.name:
                    max_len.name = len(name)
                if len(failed_tests[name][u"nics"]) > max_len.nics:
                    max_len.nics = len(failed_tests[name][u"nics"])
                if len(failed_tests[name][u"framesizes"]) > max_len.frmsizes:
                    max_len.frmsizes = len(failed_tests[name][u"framesizes"])
                if len(failed_tests[name][u"cores"]) > max_len.cores:
                    max_len.cores = len(failed_tests[name][u"cores"])

            for name, params in failed_tests.items():
                text += (
                    f"{name + u' ' * (max_len.name - len(name))}  "
                    f"{params[u'nics']}"
                    f"{u' ' * (max_len.nics - len(params[u'nics']))}  "
                    f"{params[u'framesizes']}"
                    f"{u' ' * (max_len.frmsizes-len(params[u'framesizes']))}  "
                    f"{params[u'cores']}"
                    f"{u' ' * (max_len.cores - len(params[u'cores']))}\n"
                )

            gression_hdr = (
                f"\n\n{test_set.split(u'-')[-2]}-{test_set.split(u'-')[-1]}, "
                f"CSIT build: {alert[u'urls'][idx]}/{build}, "
                f"VPP version: {version}\n\n"
            )
            # Add list of regressions:
            self._list_gressions(alert, idx, gression_hdr, u"regressions")

            # Add list of progressions:
            self._list_gressions(alert, idx, gression_hdr, u"progressions")

        text += f"\nFor detailed information visit: {alert[u'url-details']}\n"
        file_name = f"{self.configs[alert[u'way']][u'output-dir']}/" \
                    f"{self.configs[alert[u'way']][u'output-file']}"
        logging.info(f"Writing the file {file_name}.txt ...")

        try:
            with open(f"{file_name}.txt", u'w') as txt_file:
                txt_file.write(text)
        except IOError:
            logging.error(f"Not possible to write the file {file_name}.txt.")
