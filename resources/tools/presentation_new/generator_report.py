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
    padding: 0 3em;
}
.wy-menu-vertical li.toctree-l2.current > a {
    background: #c9c9c9;
    padding: 0 3em;
}
.wy-menu-vertical li.toctree-l2.current li.toctree-l3 > a {
    display: block;
    background: #c9c9c9;
    padding: 0 4em;
}
.wy-menu-vertical li.toctree-l3.current li.toctree-l4 > a {
    display: block;
    background: #bdbdbd;
    padding: 0 5em;
}
.wy-menu-vertical li.on a, .wy-menu-vertical li.current > a {
    color: #404040;
    padding: 0 2em;
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
    padding-left: 2em -4px;
}
"""

# Command to build the html format of the report
HTML_BUILDER = 'sphinx-build -v -c . -a ' \
               '-b html -E ' \
               '-t html ' \
               '-D release={release} ' \
               '-D version="Test Report {date}" ' \
               '{working_dir} ' \
               '{build_dir}/'

# Command to build the pdf format of the report
PDF_BUILDER = 'sphinx-build -v -c . -a ' \
              '-b latex -E ' \
              '-t latex ' \
              '-D release={release} ' \
              '-D version="Test Report {date}" ' \
              '{working_dir} ' \
              '{build_dir}'


def generate_report(release, spec, report_week):
    """Generate all formats and versions of the report.

    :param release: Release string of the product.
    :param spec: Specification read from the specification file.
    :param report_week: Calendar week when the report is published.
    :type release: str
    :type spec: Specification
    :type report_week: str
    """

    logging.info("Generating the report ...")

    report = {
        "html": generate_html_report,
        "pdf": generate_pdf_report
    }

    for report_format, versions in spec.output["format"].items():
        report[report_format](release, spec, versions, report_week)

    archive_input_data(spec)

    logging.info("Done.")


def generate_html_report(release, spec, versions, report_version):
    """Generate html format of the report.

    :param release: Release string of the product.
    :param spec: Specification read from the specification file.
    :param versions: List of versions to generate.
    :param report_version: Version of the report.
    :type release: str
    :type spec: Specification
    :type versions: list
    :type report_version: str
    """

    logging.info("  Generating the html report, give me a few minutes, please "
                 "...")

    working_dir = spec.environment["paths"]["DIR[WORKING,SRC]"]

    cmd = 'cd {working_dir} && mv -f index.html.template index.rst'.\
        format(working_dir=working_dir)
    execute_command(cmd)

    cmd = HTML_BUILDER.format(
        release=release,
        date=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
        working_dir=working_dir,
        build_dir=spec.environment["paths"]["DIR[BUILD,HTML]"])
    execute_command(cmd)

    with open(spec.environment["paths"]["DIR[CSS_PATCH_FILE]"], "w") as \
            css_file:
        css_file.write(THEME_OVERRIDES)

    with open(spec.environment["paths"]["DIR[CSS_PATCH_FILE2]"], "w") as \
            css_file:
        css_file.write(THEME_OVERRIDES)

    logging.info("  Done.")


def generate_pdf_report(release, spec, versions, report_week):
    """Generate html format of the report.

    :param release: Release string of the product.
    :param spec: Specification read from the specification file.
    :param versions: List of versions to generate. Not implemented yet.
    :param report_week: Calendar week when the report is published.
    :type release: str
    :type spec: Specification
    :type versions: list
    :type report_week: str
    """

    logging.info("  Generating the pdf report, give me a few minutes, please "
                 "...")

    working_dir = spec.environment["paths"]["DIR[WORKING,SRC]"]

    cmd = 'cd {working_dir} && mv -f index.pdf.template index.rst'.\
        format(working_dir=working_dir)
    execute_command(cmd)

    _convert_all_svg_to_pdf(spec.environment["paths"]["DIR[WORKING,SRC]"])

    # Convert PyPLOT graphs in HTML format to PDF.
    convert_plots = "xvfb-run -a wkhtmltopdf {html} {pdf}"
    plots = get_files(spec.environment["paths"]["DIR[STATIC,VPP]"], "html")
    plots.extend(get_files(spec.environment["paths"]["DIR[STATIC,DPDK]"],
                           "html"))
    for plot in plots:
        file_name = "{0}.pdf".format(plot.rsplit(".", 1)[0])
        logging.info("Converting '{0}' to '{1}'".format(plot, file_name))
        execute_command(convert_plots.format(html=plot, pdf=file_name))

    # Generate the LaTeX documentation
    build_dir = spec.environment["paths"]["DIR[BUILD,LATEX]"]
    cmd = PDF_BUILDER.format(
        release=release,
        date=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
        working_dir=working_dir,
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
        'cp csit.pdf ../{archive_dir}/csit_{release}.{week}.pdf &&'
        'cp csit.pdf ../{archive_dir}/csit_{release}.pdf'.
        format(build_dir=build_dir,
               archive_dir=archive_dir,
               release=release,
               week=report_week)
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


def _convert_all_svg_to_pdf(path):
    """Convert all svg files on path "path" to pdf.

    :param path: Path to the root directory with svg files to convert.
    :type path: str
    """

    cmd = "inkscape -D -z --file={svg} --export-pdf={pdf}"

    svg_files = get_files(path, "svg", full_path=True)
    for svg_file in svg_files:
        pdf_file = "{0}.pdf".format(svg_file.rsplit('.', 1)[0])
        logging.info("Converting '{0}' to '{1}'".format(svg_file, pdf_file))
        execute_command(cmd.format(svg=svg_file, pdf=pdf_file))
