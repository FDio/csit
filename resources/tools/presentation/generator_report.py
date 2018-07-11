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

import logging
import datetime

from shutil import make_archive

from utils import get_files, execute_command, archive_input_data


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
.rst-content blockquote {
    margin-left: 0px;
    line-height: 18px;
    margin-bottom: 0px;
}
.wy-menu-vertical a {
    display: inline-block;
    line-height: 18px;
    padding: 0 2em;
    display: block;
    position: relative;
    font-size: 90%;
    color: #d9d9d9
}
.wy-menu-vertical li.current a {
    color: gray;
    border-right: solid 1px #c9c9c9;
    padding: 0 2.427em;
.wy-menu-vertical li.toctree-l2.current li.toctree-l3 > a {
    display: block;
    background: #c9c9c9;
    padding: 0 4.045em;
}
.wy-menu-vertical li.on a, .wy-menu-vertical li.current > a {
    color: #404040;
    padding: 0 1.618em;
    font-weight: bold;
    position: relative;
    background: #fcfcfc;
    border: none;
        border-top-width: medium;
        border-bottom-width: medium;
        border-top-style: none;
        border-bottom-style: none;
        border-top-color: currentcolor;
        border-bottom-color: currentcolor;
    padding-left: 1.618em -4px;
}
"""

# Command to build the html format of the report
HTML_BUILDER = 'sphinx-build -v -c . -a ' \
               '-b html -E ' \
               '-t html ' \
               '-D release={release} ' \
               '-D version="Report v0.1 - {date}" ' \
               '{working_dir} ' \
               '{build_dir}/'

# Command to build the pdf format of the report
PDF_BUILDER = 'sphinx-build -v -c . -a ' \
              '-b latex -E ' \
              '-t latex ' \
              '-D release={release} ' \
              '-D version="{release} report - {date}" ' \
              '{working_dir} ' \
              '{build_dir}'


def generate_report(release, spec):
    """Generate all formats and versions of the report.

    :param release: Release string of the product.
    :param spec: Specification read from the specification file.
    :type release: str
    :type spec: Specification
    """

    logging.info("Generating the report ...")

    report = {
        "html": generate_html_report,
        "pdf": generate_pdf_report
    }

    for report_format, versions in spec.output["format"].items():
        report[report_format](release, spec, versions)

    archive_input_data(spec)
    archive_report(spec)

    logging.info("Done.")


def generate_html_report(release, spec, versions):
    """Generate html format of the report.

    :param release: Release string of the product.
    :param spec: Specification read from the specification file.
    :param versions: List of versions to generate.
    :type release: str
    :type spec: Specification
    :type versions: list
    """

    logging.info("  Generating the html report, give me a few minutes, please "
                 "...")

    cmd = HTML_BUILDER.format(
        release=release,
        date=datetime.datetime.utcnow().strftime('%m/%d/%Y %H:%M UTC'),
        working_dir=spec.environment["paths"]["DIR[WORKING,SRC]"],
        build_dir=spec.environment["paths"]["DIR[BUILD,HTML]"])
    execute_command(cmd)

    with open(spec.environment["paths"]["DIR[CSS_PATCH_FILE]"], "w") as \
            css_file:
        css_file.write(THEME_OVERRIDES)

    with open(spec.environment["paths"]["DIR[CSS_PATCH_FILE2]"], "w") as \
            css_file:
        css_file.write(THEME_OVERRIDES)

    logging.info("  Done.")


def generate_pdf_report(release, spec, versions):
    """Generate html format of the report.

    :param release: Release string of the product.
    :param spec: Specification read from the specification file.
    :param versions: List of versions to generate. Not implemented yet.
    :type release: str
    :type spec: Specification
    :type versions: list
    """

    logging.info("  Generating the pdf report, give me a few minutes, please "
                 "...")

    convert_plots = "xvfb-run -a wkhtmltopdf {html} {pdf}.pdf"

    # Convert PyPLOT graphs in HTML format to PDF.
    plots = get_files(spec.environment["paths"]["DIR[STATIC,VPP]"], "html")
    plots.extend(get_files(spec.environment["paths"]["DIR[STATIC,DPDK]"],
                           "html"))
    for plot in plots:
        file_name = "{0}".format(plot.rsplit(".", 1)[0])
        cmd = convert_plots.format(html=plot, pdf=file_name)
        execute_command(cmd)

    # Generate the LaTeX documentation
    build_dir = spec.environment["paths"]["DIR[BUILD,LATEX]"]
    cmd = PDF_BUILDER.format(
        release=release,
        date=datetime.datetime.utcnow().strftime('%m/%d/%Y %H:%M UTC'),
        working_dir=spec.environment["paths"]["DIR[WORKING,SRC]"],
        build_dir=build_dir)
    execute_command(cmd)

    # Build pdf documentation
    archive_dir = spec.environment["paths"]["DIR[STATIC,ARCH]"]
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
        execute_command(cmd)

    logging.info("  Done.")


def archive_report(spec):
    """Archive the report.

    :param spec: Specification read from the specification file.
    :type spec: Specification
    """

    logging.info("  Archiving the report ...")

    make_archive("csit.report",
                 "gztar",
                 base_dir=spec.environment["paths"]["DIR[BUILD,HTML]"])

    logging.info("  Done.")
