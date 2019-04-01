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
import csv

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os.path import isdir
from collections import OrderedDict

from utils import execute_command
from errors import PresentationError


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

        try:
            self._spec = spec.alerting
        except KeyError as err:
            raise  AlertingError("Alerting is not configured, skipped.",
                                 repr(err),
                                 "WARNING")

        self._path_failed_tests = spec.environment["paths"]["DIR[STATIC,VPP]"]

        # Verify and validate input specification:
        self.configs = self._spec.get("configurations", None)
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

        self.alerts = self._spec.get("alerts", None)
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
            if alert_data["way"] == "email":
                text, html = self._create_alert_message(alert_data)
                conf = self.configs["email"]
                self._send_email(server=conf["server"],
                                 addr_from=conf["address-from"],
                                 addr_to=conf["address-to"],
                                 subject=alert_data["title"],
                                 text=text,
                                 html=html)
            elif alert_data["way"] == "jenkins":
                # TODO: Remove when not needed
                self._generate_files_for_jenkins(alert_data)
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

    def _create_alert_message(self, alert):
        """Create the message which is used in the generated alert.

        :param alert: Message is created for this alert.
        :type alert: dict
        :returns: Message in the ASCII text and HTML format.
        :rtype: tuple(str, str)
        """

        if alert["type"] == "failed-tests":
            text = ""
            html = "<html><body>"
            for item in alert["include"]:
                file_name = "{path}/{name}".format(
                    path=self._path_failed_tests, name=item)
                try:
                    with open("{0}.txt".format(file_name), 'r') as txt_file:
                        text += "{0}:\n\n".format(
                            item.replace("failed-tests-", ""))
                        text += txt_file.read() + "\n" * 2
                except IOError:
                    logging.error("Not possible to read the file '{0}.txt'.".
                                  format(file_name))
                try:
                    with open("{0}.rst".format(file_name), 'r') as rst_file:
                        html += "<h2>{0}:</h2>".format(
                            item.replace("failed-tests-", ""))
                        html += rst_file.readlines()[2].\
                            replace("../trending", alert.get("url", ""))
                        html += "<br>" * 3
                except IOError:
                    logging.error("Not possible to read the file '{0}.rst'.".
                                  format(file_name))
            html += "</body></html>"
        else:
            raise AlertingError("Alert of type '{0}' is not implemented.".
                                format(alert["type"]))
        return text, html

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
        :returns: Compressed failed tests.
        :rtype: OrderedDict
        """

        directory = self.configs[alert["way"]]["output-dir"]
        failed_tests = OrderedDict()
        with open("{0}/{1}.csv".format(directory, test_set), 'rb') as csv_file:
            for row in csv.reader(csv_file, delimiter=',', quotechar='"'):
                logging.info(row)
                try:
                    test = row[0].split('-')
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
                if not nic in failed_tests[name]["nics"]:
                    failed_tests[name]["nics"].append(nic)
                if not framesize in failed_tests[name]["framesizes"]:
                    failed_tests[name]["framesizes"].append(framesize)
                if not cores in failed_tests[name]["cores"]:
                    failed_tests[name]["cores"].append(cores)
        if sort:
            sorted_failed_tests = OrderedDict()
            keys = [k for k in failed_tests.keys()]
            keys.sort()
            for key in keys:
                sorted_failed_tests[key] = failed_tests[key]
            return sorted_failed_tests
        else:
            return failed_tests

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
        for test_set in alert.get("include", []):
            text += "\n\n{0}\n\n".format(test_set)
            failed_tests = self._get_compressed_failed_tests(alert, test_set)
            for name, params in failed_tests.items():
                text += "{name} ({nics}, {frames}, {cores})\n".format(
                    name=name,
                    nics=", ".join(params["nics"]),
                    frames=", ".join(params["framesizes"]),
                    cores=", ".join(params["cores"]))

        file_name = "{0}/compressed-{1}".format(config["output-dir"],
                                                config["output-file"])
        logging.info("Writing the file '{0}.txt' ...".format(file_name))

        try:
            with open("{0}.txt".format(file_name), 'w') as txt_file:
                txt_file.write(text)
        except IOError:
            logging.error("Not possible to write the file '{0}.txt'.".
                          format(file_name))

    def _generate_files_for_jenkins(self, alert):
        """Create the file which is used in the generated alert.

        # TODO: Remove when not needed.

        :param alert: Files are created for this alert.
        :type alert: dict
        """

        config = self.configs[alert["way"]]

        if alert["type"] == "failed-tests":
            text, html = self._create_alert_message(alert)
            file_name = "{0}/{1}".format(config["output-dir"],
                                         config["output-file"])
            logging.info("Writing the file '{0}.txt' ...".format(file_name))
            try:
                with open("{0}.txt".format(file_name), 'w') as txt_file:
                    txt_file.write(text)
            except IOError:
                logging.error("Not possible to write the file '{0}.txt'.".
                              format(file_name))
            logging.info("Writing the file '{0}.html' ...".format(file_name))
            try:
                with open("{0}.html".format(file_name), 'w') as html_file:
                    html_file.write(html)
            except IOError:
                logging.error("Not possible to write the file '{0}.html'.".
                              format(file_name))

            zip_file = config.get("zip-output", None)
            if zip_file:
                logging.info("Writing the file '{0}/{1}' ...".
                             format(config["output-dir"], zip_file))
                execute_command("tar czvf {dir}/{zip} --directory={dir} "
                                "{input}.txt {input}.html".
                                format(dir=config["output-dir"],
                                       zip=zip_file,
                                       input=config["output-file"]))
        else:
            raise AlertingError("Alert of type '{0}' is not implemented.".
                                format(alert["type"]))
