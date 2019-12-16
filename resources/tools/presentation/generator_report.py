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

"""Report generation.
"""

import logging
import datetime

from shutil import make_archive

from pal_utils import get_files, execute_command, archive_input_data


# Command to build the html format of the report
HTML_BUILDER = u'sphinx-build -v -c . -a ' \
               u'-b html -E ' \
               u'-t html ' \
               u'-D release={release} ' \
               u'-D version="Test Report {date}" ' \
               u'{working_dir} ' \
               u'{build_dir}/'

# Command to build the pdf format of the report
PDF_BUILDER = u'sphinx-build -v -c . -a ' \
              u'-b latex -E ' \
              u'-t latex ' \
              u'-D release={release} ' \
              u'-D version="Test Report {date}" ' \
              u'{working_dir} ' \
              u'{build_dir}'


def generate_report(release, spec, report_week):
    """Generate all formats and versions of the report.

    :param release: Release string of the product.
    :param spec: Specification read from the specification file.
    :param report_week: Calendar week when the report is published.
    :type release: str
    :type spec: Specification
    :type report_week: str
    """

    logging.info(u"Generating the report ...")

    report = {
        u"html": generate_html_report,
        u"pdf": generate_pdf_report
    }

    for report_format in spec.output[u"format"]:
        report[report_format](release, spec, report_week)

    archive_input_data(spec)

    logging.info(u"Done.")


def generate_html_report(release, spec, report_version):
    """Generate html format of the report.

    :param release: Release string of the product.
    :param spec: Specification read from the specification file.
    :param report_version: Version of the report.
    :type release: str
    :type spec: Specification
    :type report_version: str
    """

    _ = report_version

    logging.info(u"  Generating the html report, give me a few minutes, please "
                 u"...")

    working_dir = spec.environment[u"paths"][u"DIR[WORKING,SRC]"]

    execute_command(f"cd {working_dir} && mv -f index.html.template index.rst")

    cmd = HTML_BUILDER.format(
        release=release,
        date=datetime.datetime.utcnow().strftime(u'%Y-%m-%d %H:%M UTC'),
        working_dir=working_dir,
        build_dir=spec.environment[u"paths"][u"DIR[BUILD,HTML]"])
    execute_command(cmd)

    logging.info(u"  Done.")


def generate_pdf_report(release, spec, report_week):
    """Generate html format of the report.

    :param release: Release string of the product.
    :param spec: Specification read from the specification file.
    :param report_week: Calendar week when the report is published.
    :type release: str
    :type spec: Specification
    :type report_week: str
    """

    logging.info(u"  Generating the pdf report, give me a few minutes, please "
                 u"...")

    working_dir = spec.environment[u"paths"][u"DIR[WORKING,SRC]"]

    execute_command(f"cd {working_dir} && mv -f index.pdf.template index.rst")

    _convert_all_svg_to_pdf(spec.environment[u"paths"][u"DIR[WORKING,SRC]"])

    # Convert PyPLOT graphs in HTML format to PDF.
    convert_plots = u"xvfb-run -a wkhtmltopdf {html} {pdf}"
    plots = get_files(spec.environment[u"paths"][u"DIR[STATIC,VPP]"], u"html")
    plots.extend(
        get_files(spec.environment[u"paths"][u"DIR[STATIC,DPDK]"], u"html")
    )
    for plot in plots:
        file_name = f"{plot.rsplit(u'.', 1)[0]}.pdf"
        logging.info(f"Converting {plot} to {file_name}")
        execute_command(convert_plots.format(html=plot, pdf=file_name))

    # Generate the LaTeX documentation
    build_dir = spec.environment[u"paths"][u"DIR[BUILD,LATEX]"]
    cmd = PDF_BUILDER.format(
        release=release,
        date=datetime.datetime.utcnow().strftime(u'%Y-%m-%d %H:%M UTC'),
        working_dir=working_dir,
        build_dir=build_dir)
    execute_command(cmd)

    # Build pdf documentation
    archive_dir = spec.environment[u"paths"][u"DIR[STATIC,ARCH]"]
    cmds = [
        f'cd {build_dir} && '
        f'pdflatex -shell-escape -interaction nonstopmode csit.tex || true',
        f'cd {build_dir} && '
        f'pdflatex -interaction nonstopmode csit.tex || true',
        f'cd {build_dir} && '
        f'cp csit.pdf ../{archive_dir}/csit_{release}.{report_week}.pdf &&'
        f'cp csit.pdf ../{archive_dir}/csit_{release}.pdf'
    ]

    for cmd in cmds:
        execute_command(cmd)

    logging.info(u"  Done.")


def archive_report(spec):
    """Archive the report.

    :param spec: Specification read from the specification file.
    :type spec: Specification
    """

    logging.info(u"  Archiving the report ...")

    make_archive(
        u"csit.report",
        u"gztar",
        base_dir=spec.environment[u"paths"][u"DIR[BUILD,HTML]"]
    )

    logging.info(u"  Done.")


def _convert_all_svg_to_pdf(path):
    """Convert all svg files on path "path" to pdf.

    :param path: Path to the root directory with svg files to convert.
    :type path: str
    """

    svg_files = get_files(path, u"svg", full_path=True)
    for svg_file in svg_files:
        pdf_file = f"{svg_file.rsplit(u'.', 1)[0]}.pdf"
        logging.info(f"Converting {svg_file} to {pdf_file}")
        execute_command(
            f"inkscape -D -z --file={svg_file} --export-pdf={pdf_file}"
        )
