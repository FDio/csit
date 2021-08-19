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

    WORKING_DIR="tmp"
    BUILD_DIR="_build"

    # Create working directories
    mkdir "${BUILD_DIR}"
    mkdir --parents "${WORKING_DIR}"/resources/libraries/python/
    mkdir --parents "${WORKING_DIR}"/resources/libraries/robot/
    mkdir --parents "${WORKING_DIR}"/tests/

    # Copy the Sphinx source files:
    cp -r src/* ${WORKING_DIR}/

    # Copy the source files to be processed:
    from_dir="../../../resources/libraries/python/"
    to_dir="${WORKING_DIR}/resources/libraries/python/"
    command="rsync -a --include '*/'"
    ${command} --include '*.py' --exclude '*' "${from_dir}" "${to_dir}"
    cp ../../../resources/__init__.py ${WORKING_DIR}/resources/
    cp ../../../resources/libraries/__init__.py ${WORKING_DIR}/resources/libraries/
    from_dir="../../../resources/libraries/robot/"
    to_dir="${WORKING_DIR}/resources/libraries/robot/"
    ${command} --include '*.robot' --exclude '*' "${from_dir}" "${to_dir}"
    from_dir="../../../tests/"
    to_dir="${WORKING_DIR}/tests/"
    ${command} --include '*.robot' --exclude '*' "${from_dir}" "${to_dir}"

    python3 gen_rst.py
    # Remove all rst files from ./${WORKING_DIR}/env directory - we do not need
    # them
    find ./${WORKING_DIR}/env -type f -name '*.rst' | xargs rm -f

    # Generate the documentation:
    DATE=$(date -u '+%d-%b-%Y')

    all_options=("-v")
    all_options+=("-c" "${WORKING_DIR}")
    all_options+=("-a")
    all_options+=("-b" "html")
    all_options+=("-E")
    all_options+=("-D" "release=$1")
    all_options+=("-D" "version='$1 documentation - $DATE'")
    all_options+=("${WORKING_DIR}" "${BUILD_DIR}/")

    set +e
    sphinx-build "${all_options[@]}"
    DOCS_EXIT_STATUS="$?"
    set -e

    find . -type d -name 'env' | xargs rm -rf

}

function generate_report () {

    # Generate report content.
    #
    # Variable read:
    # - ${TOOLS_DIR} - Path to existing resources subdirectory "tools".
    # - ${GERRIT_BRANCH} - Gerrit branch used for release tagging.
    # - ${CSIT_REPORT_FILENAME} - Source filename, optional.
    # - ${CSIT_REPORT_DIRECTORYNAME} - Source directory, optional.
    # - ${CSIT_REPORT_SPECIFICATION} - Specification to use, optional.
    # - ${RELEASE} - Alternative to GERRIT_BRANCH for overriding release tag.
    # - ${WEEK} - Optional override for week number.
    # Variables set:
    # - DOCS_EXIT_STATUS - Exit status of report generation.
    # Variables exported:
    # - PYTHONPATH - Added a dir, never removed here.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${TOOLS_DIR}"/presentation || die "Pushd failed!"

    filename="${CSIT_REPORT_FILENAME:-}"
    directoryname="${CSIT_REPORT_DIRECTORYNAME:-}"
    spec="${CSIT_REPORT_SPECIFICATION:-report}"
    branch="${GERRIT_BRANCH:-master}"
    release_tag="${RELEASE:-$branch}"
    week_number=$(date "+%V")
    week_number="${WEEK:-$week_number}"

    # Set default values in config array.
    typeset -A CFG
    typeset -A DIR

    DIR[WORKING]="_tmp"

    # Create working directories.
    mkdir "${DIR[WORKING]}" || die "Mkdir failed!"

    export PYTHONPATH=`pwd`:`pwd`/../../../ || die "Export failed!"

    all_options=("pal.py")
    all_options+=("--specification" "specifications/${spec}")
    all_options+=("--release" "${release_tag}")
    all_options+=("--week" "${week_number}")
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

function generate_report_local () {

    # Sudo-install apt dependencies, then generate report from local content.
    #
    # Also, patch the LaTeX installation to allow more memory.
    #
    # Variable read:
    # - ${TOOLS_DIR} - Path to existing resources subdirectory "tools".
    # - ${CSIT_REPORT_FILENAME} - Source filename, optional.
    # - ${CSIT_REPORT_DIRECTORYNAME} - Source directory, optional.
    # - ${CSIT_REPORT_INSTALL_DEPENDENCIES} - Whether to install dependencies.
    # - ${CSIT_REPORT_INSTALL_LATEX} - Whether to install latex.
    # - ${CSIT_REPORT_SPECIFICATION} - Specification to use, optional.
    # - ${RELEASE} - Alternative to GERRIT_BRANCH for overriding release tag.
    # - ${WEEK} - Optional override for week number.
    # Variables set:
    # - DOCS_EXIT_STATUS - Exit status of report generation.
    # Variables exported:
    # - PYTHONPATH - Added a dir, never removed here.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    install_dependencies="${CSIT_REPORT_INSTALL_DEPENDENCIES:-1}"
    install_latex="${CSIT_REPORT_INSTALL_LATEX:-0}"

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

    generate_report
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
