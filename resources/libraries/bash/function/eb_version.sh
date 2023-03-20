#!/usr/bin/env bash

# Copyright (c) 2023 Cisco and/or its affiliates.
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


function die_on_error () {

    # Source this fragment if you want to abort on any failure.
    #
    # Variables read:
    # - CODE_EXIT_STATUS - Exit status of report generation.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if [[ "${CODE_EXIT_STATUS}" != "0" ]]; then
        die "Failed to generate docs!" "${CODE_EXIT_STATUS}"
    fi
}


function eb_version_deploy () {

    # Deploy Elastic Beanstalk CDash content.
    #
    # Variable read:
    # - ${CSIT_DIR} - CSIT main directory.
    # - ${TERRAFORM_OUTPUT_VAL} - Terraform output value.
    # Variables set:
    # - CODE_EXIT_STATUS - Exit status of report generation.
    # - TERRAFORM_OUTPUT_VAR - Register Terraform output variable name.
    # Functions called:
    # - eb_version_verify - Build and verify EB version.
    # - terraform_apply - Apply EB version by Terraform.
    # - terraform_output - Get the application name string from Terraform.
    # - die - Print to stderr and exit.

    set -exuo pipefail

    eb_version_verify || die "Failed to call Elastic Beanstalk verify!"
    terraform_apply || die "Failed to call Terraform apply!"

    TERRAFORM_OUTPUT_VAR="application_version"
    terraform_output || die "Failed to call Terraform output!"

    #aws --region eu-central-1 elasticbeanstalk update-environment \
    #    --environment-name fdio-csit-dash-env \
    #    --version-label "${TERRAFORM_OUTPUT_VAL}"
}


function eb_version_verify () {

    # Build and verify Elastic Beanstalk CDash integrity.
    #
    # Variable read:
    # - ${CSIT_DIR} - CSIT main directory.
    # Variables set:
    # - TERRAFORM_MODULE_DIR - Terraform module sub-directory.
    # Functions called:
    # - hugo_init_modules - Initialize Hugo modules.
    # - hugo_build_site - Build static site with Hugo.
    # - terraform_init - Initialize Terraform modules.
    # - terraform_validate - Validate Terraform code.
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if ! installed zip; then
        die "Please install zip!"
    fi

    pushd "${CSIT_DIR}"/csit.infra.dash || die "Pushd failed!"
    pushd app || die "Pushd failed!"
    find . -type d -name "__pycache__" -exec rm -rf "{}" \;
    find . -type d -name ".webassets-cache" -exec rm -rf "{}" \;
    zip -r ../app.zip . || die "Compress failed!"
    popd || die "Popd failed!"
    popd || die "Popd failed!"

    TERRAFORM_MODULE_DIR="terraform-aws-fdio-csit-dash-app-base"

    export TF_VAR_application_version="${BUILD_ID-50}"
    hugo_init_modules || die "Failed to call Hugo initialize!"
    hugo_build_site || die "Failed to call Hugo build!"
    terraform_init || die "Failed to call terraform init!"
    terraform_validate || die "Failed to call terraform validate!"
}


function generate_report () {

    # Generate report content.
    #
    # Variable read:
    # - ${TOOLS_DIR} - Path to existing resources subdirectory "tools".
    # - ${GERRIT_BRANCH} - Gerrit branch used for release tagging.
    # Variables set:
    # - CODE_EXIT_STATUS - Exit status of report generation.
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
    CODE_EXIT_STATUS="$?"
    set -e
}

function installed () {

    # Check if the given utility is installed. Fail if not installed.
    #
    # Arguments:
    # - ${1} - Utility to check.
    # Returns (implicitly):
    # - 0 - If command is installed.
    # - 1 - If command is not installed.

    set -exuo pipefail

    command -v "${1}"
}
