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

"""Report generation.
"""

import subprocess
import logging
import datetime

from os import makedirs, environ
from os.path import isdir
from shutil import copy, Error, make_archive

from utils import get_files
from errors import PresentationError


# .css file for the html format of the report
THEME_OVERRIDES = """/* override table width restrictions */
@media screen and (min-width: 767px) {
    .wy-table-responsive table td, .wy-table-responsive table th {
        white-space: normal !important;
    }

    .wy-table-responsive {
        font-size: small;
        margin-bottom: 24px;
        max-width: 100%;
        overflow: visible !important;
    }
}
"""

# Command to build the html format of the report
HTML_BUILDER = 'sphinx-build -v -c . -a ' \
               '-b html -E ' \
               '-D release={release} ' \
               '-D version="{release} report - {date}" ' \
               '{working_dir} ' \
               '{build_dir}/'

# Command to build the pdf format of the report
PDF_BUILDER = 'sphinx-build -v -c . -a ' \
              '-b latex -E ' \
              '-D release={release} ' \
              '-D version="{release} report - {date}" ' \
              '{working_dir} ' \
              '{build_dir}'


def generate_report(release, config):
    """Generate all formats and versions of the report.

    :param release: Release string of the product.
    :param config: Configuration read from the specification file.
    :type release: str
    :type config: Configuration
    """

    logging.info("Generating the report ...")

    report = {
        "html": generate_html_report,
        "pdf": generate_pdf_report
    }

    for report_format, versions in config.output.items():
        report[report_format](release, config, versions)

    archive_input_data(config)
    archive_report(config)

    logging.info("Done.")


def generate_html_report(release, config, versions):
    """Generate html format of the report.

    :param release: Release string of the product.
    :param config: Configuration read from the specification file.
    :param versions: List of versions to generate.
    :type release: str
    :type config: Configuration
    :type versions: list
    """

    logging.info("  Generating the html report, give me a few minutes, please "
                 "...")

    cmd = HTML_BUILDER.format(
        release=release,
        date=datetime.date.today().strftime('%d-%b-%Y'),
        working_dir=config.environment["paths"]["DIR[WORKING,SRC]"],
        build_dir=config.environment["paths"]["DIR[BUILD,HTML]"])
    _execute_command(cmd)

    with open(config.environment["paths"]["DIR[CSS_PATCH_FILE]"], "w") as \
            css_file:
        css_file.write(THEME_OVERRIDES)

    logging.info("  Done.")


def generate_pdf_report(release, config, versions):
    """Generate html format of the report.

    :param release: Release string of the product.
    :param config: Configuration read from the specification file.
    :param versions: List of versions to generate.
    :type release: str
    :type config: Configuration
    :type versions: list
    """

    logging.info("  Generating the pdf report, give me a few minutes, please "
                 "...")

    convert_plots = "xvfb-run -a wkhtmltopdf {html} {pdf}.pdf"

    # Convert PyPLOT graphs in HTML format to PDF.
    plots  = get_files(config.environment["paths"]["DIR[STATIC,VPP]"], "html")
    for plot in plots:
        file_name = "{0}.pdf".format(plot.rsplit(".", 1)[0])
        cmd = convert_plots.format(html=plot, pdf=file_name)
        _execute_command(cmd)

    # Generate the LaTeX documentation
    build_dir = config.environment["paths"]["DIR[BUILD,LATEX]"]
    cmd = PDF_BUILDER.format(
        release=release,
        date=datetime.date.today().strftime('%d-%b-%Y'),
        working_dir=config.environment["paths"]["DIR[WORKING,SRC]"],
        build_dir=build_dir)
    _execute_command(cmd)

    # Build pdf documentation
    archive_dir = config.environment["paths"]["DIR[STATIC,ARCH]"]
    cmds = [
        'cd {build_dir} && '
        'pdflatex -shell-escape -interaction nonstopmode csit.tex || true'.
        format(build_dir=build_dir),
        'cd {build_dir} && '
        'pdflatex -interaction nonstopmode csit.tex || true'.
        format(build_dir=build_dir),
        'cd {build_dir} && '
        'cp csit.pdf ../{archive_dir}/csit_{release}.pdf'.
        format(build_dir=build_dir,
               archive_dir=archive_dir,
               release=release)
    ]

    for cmd in cmds:
        _execute_command(cmd)

    logging.info("  Done.")


def archive_report(config):
    """Archive the report.

    :param config: Configuration read from the specification file.
    :type config: Configuration
    """

    logging.info("  Archiving the report ...")

    make_archive("csit.report",
                 "gztar",
                 base_dir=config.environment["paths"]["DIR[BUILD,HTML]"])

    logging.info("  Done.")


def archive_input_data(config):
    """Archive the report.

    :param config: Configuration read from the specification file.
    :type config: Configuration
    :raises PresentationError: If it is not possible to archive the input data.
    """

    logging.info("    Archiving the input data files ...")

    data_files = get_files(config.environment["paths"]["DIR[WORKING,DATA]"],
                           extension=config.input["general"]["file-format"])
    dst = config.environment["paths"]["DIR[STATIC,ARCH]"]
    logging.info("      Destination: {0}".format(dst))

    try:
        if not isdir(dst):
            makedirs(dst)

        for data_file in data_files:
            logging.info("      Copying the file: {0} ...".format(data_file))
            copy(data_file, dst)

    except (Error, OSError) as err:
        raise PresentationError("Not possible to archive the input data.",
                                str(err))

    logging.info("    Done.")


def _execute_command(cmd):
    """Execute the command in a subprocess and log the stdout and stderr.

    :param cmd: Command to execute.
    :type cmd: str
    :returns: Return code of the executed command.
    :rtype: int
    """

    env = environ.copy()
    proc = subprocess.Popen(
        [cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        env=env)

    stdout, stderr = proc.communicate()

    logging.info(stdout)
    logging.info(stderr)

    if proc.returncode != 0:
        logging.error("    Command execution failed.")
    return proc.returncode
