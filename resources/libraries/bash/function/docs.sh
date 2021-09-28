#!/usr/bin/env bash

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

set -exuo pipefail


function die_on_docs_error () {

    # Source this fragment if you want to abort on any failure.
    #
    # Variables read:
    # - DOCS_EXIT_STATUS - Set by a generation function.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if [[ "${DOCS_EXIT_STATUS}" != "0" ]]; then
        die "Failed to generate docs!" "${DOCS_EXIT_STATUS}"
    fi
}

function generate_docs () {

    # Generate docs content.
    #
    # Variable read:
    # - ${TOOLS_DIR} - Path to existing resources subdirectory "tools".
    # Variables set:
    # - DOCS_EXIT_STATUS - Exit status of docs generation.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${TOOLS_DIR}"/doc_gen || die "Pushd failed!"

    export WORKING_DIR=$(mktemp -d /tmp/tmp-csitXXX)
    BUILD_DIR="_build"

    # Remove the old build:
    rm -rf ${BUILD_DIR} || true
    rm -rf /tmp/tmp-csit* || true

    # Create working directories
    mkdir -p "${BUILD_DIR}" || die "Mkdir failed!"
    mkdir -p "${WORKING_DIR}"/resources/libraries/python/ || die "Mkdir failed!"
    mkdir -p "${WORKING_DIR}"/resources/libraries/robot/ || die "Mkdir failed!"
    mkdir -p "${WORKING_DIR}"/tests/ || die "Mkdir failed!"

    # Copy the Sphinx source files:
    cp -r src/* ${WORKING_DIR}/ || die "Copy the Sphinx source files failed!"

    # Copy the source files to be processed:
    from_dir="${RESOURCES_DIR}/libraries/python/"
    to_dir="${WORKING_DIR}/resources/libraries/python/"
    dirs="${from_dir} ${to_dir}"
    rsync -ar --include='*/' --include='*.py' --exclude='*' ${dirs} || {
        die "rSync failed!"
    }

    from_dir="${RESOURCES_DIR}/libraries/robot/"
    to_dir="${WORKING_DIR}/resources/libraries/robot/"
    dirs="${from_dir} ${to_dir}"
    rsync -ar --include='*/' --include '*.robot' --exclude '*' ${dirs} || {
        die "rSync failed!"
    }
    touch ${to_dir}/index.robot || {
        die "Touch index.robot file failed!"
    }

    from_dir="${CSIT_DIR}/tests/"
    to_dir="${WORKING_DIR}/tests/"
    dirs="${from_dir} ${to_dir}"
    rsync -ar --include='*/' --include '*.robot' --exclude '*' ${dirs} || {
        die "rSync failed!"
    }

    find ${WORKING_DIR}/ -type d -exec echo {} \; -exec touch {}/__init__.py \;

    python3 gen_rst.py || die "Generate .rst files failed!"

    # Generate the documentation:
    DATE=$(date -u '+%d-%b-%Y') || die "Get date failed!"

    all_options=("-v")
    all_options+=("-c" "${WORKING_DIR}")
    all_options+=("-a")
    all_options+=("-b" "html")
    all_options+=("-E")
    all_options+=("-D" "version="${GERRIT_BRANCH:-master}"")
    all_options+=("${WORKING_DIR}" "${BUILD_DIR}/")

    set +e
    sphinx-build "${all_options[@]}"
    DOCS_EXIT_STATUS="$?"
    set -e
}

function generate_report () {

    # Generate report content.
    #
    # Variable read:
    # - ${TOOLS_DIR} - Path to existing resources subdirectory "tools".
    # - ${GERRIT_BRANCH} - Gerrit branch used for release tagging.
    # Variables set:
    # - DOCS_EXIT_STATUS - Exit status of report generation.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${TOOLS_DIR}"/presentation || die "Pushd failed!"

    # Set default values in config array.
    typeset -A CFG
    typeset -A DIR

    DIR[WORKING]="_tmp"

    # Create working directories.
    mkdir "${DIR[WORKING]}" || die "Mkdir failed!"

    export PYTHONPATH=`pwd`:`pwd`/../../../ || die "Export failed!"

    all_options=("pal.py")
    all_options+=("--specification" "specifications/report")
    all_options+=("--release" "${GERRIT_BRANCH:-master}")
    all_options+=("--week" $(date "+%V"))
    all_options+=("--logging" "INFO")
    all_options+=("--force")

    set +e
    python "${all_options[@]}"
    DOCS_EXIT_STATUS="$?"
    set -e

}

function generate_report_local () {

    # Generate report from local content.
    #
    # Variable read:
    # - ${TOOLS_DIR} - Path to existing resources subdirectory "tools".
    # - ${CSIT_REPORT_FILENAME} - Source filename.
    # - ${CSIT_REPORT_DIRECTORYNAME} - Source directory.
    # - ${CSIT_REPORT_INSTALL_DEPENDENCIES} - Whether to install dependencies.
    # - ${CSIT_REPORT_INSTALL_LATEX} - Whether to install latex.
    # Variables set:
    # - DOCS_EXIT_STATUS - Exit status of report generation.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${TOOLS_DIR}"/presentation || die "Pushd failed!"

    filename="${CSIT_REPORT_FILENAME-}"
    directoryname="${CSIT_REPORT_DIRECTORYNAME-}"
    install_dependencies="${CSIT_REPORT_INSTALL_DEPENDENCIES:-1}"
    install_latex="${CSIT_REPORT_INSTALL_LATEX:-0}"

    # Set default values in config array.
    typeset -A CFG
    typeset -A DIR

    DIR[WORKING]="_tmp"

    # Install system dependencies.
    if [[ ${install_dependencies} -eq 1 ]] ;
    then
        sudo apt -y update || die "APT update failed!"
        sudo apt -y install libxml2 libxml2-dev libxslt-dev \
            build-essential zlib1g-dev unzip || die "APT install failed!"
    fi

    if [[ ${install_latex} -eq 1 ]] ;
    then
        sudo apt -y update || die "APT update failed!"
        sudo apt -y install xvfb texlive-latex-recommended \
            texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra \
            latexmk wkhtmltopdf inkscape || die "APT install failed!"
        target="/usr/share/texlive/texmf-dist/web2c/texmf.cnf"
        sudo sed -i.bak 's/^\(main_memory\s=\s\).*/\110000000/' "${target}" || {
            die "Patching latex failed!"
        }
    fi

    # Create working directories.
    mkdir "${DIR[WORKING]}" || die "Mkdir failed!"

    export PYTHONPATH=`pwd`:`pwd`/../../../ || die "Export failed!"

    all_options=("pal.py")
    all_options+=("--specification" "specifications/report_local")
    all_options+=("--release" "${RELEASE:-master}")
    all_options+=("--week" "${WEEK:-1}")
    all_options+=("--logging" "INFO")
    all_options+=("--force")
    if [[ ${filename} != "" ]]; then
        all_options+=("--input-file" "${filename}")
    fi
    if [[ ${directoryname} != "" ]]; then
        all_options+=("--input-directory" "${directoryname}")
    fi

    set +e
    python "${all_options[@]}"
    DOCS_EXIT_STATUS="$?"
    set -e

}

function generate_trending () {

    # Generate trending content.
    #
    # Variable read:
    # - ${TOOLS_DIR} - Path to existing resources subdirectory "tools".
    # Variables set:
    # - DOCS_EXIT_STATUS - Exit status of trending generation.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${TOOLS_DIR}"/presentation || die "Pushd failed!"

    # Set default values in config array.
    typeset -A DIR

    DIR[WORKING]="_tmp"

    # Create working directories.
    mkdir "${DIR[WORKING]}" || die "Mkdir failed!"

    export PYTHONPATH=`pwd`:`pwd`/../../../ || die "Export failed!"

    all_options=("pal.py")
    all_options+=("--specification" "specifications/trending")
    all_options+=("--logging" "INFO")
    all_options+=("--force")

    set +e
    python "${all_options[@]}"
    DOCS_EXIT_STATUS="$?"
    set -e

}
