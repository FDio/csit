#!/usr/bin/env bash

set -xuo pipefail

command -v zip || exit 1

rm -f app.zip

pushd app
find . -type d -name "__pycache__" -exec rm -rf "{}" \;
find . -type d -name ".webassets-cache" -exec rm -rf "{}" \;
zip -r ../app.zip .
popd

pushd "../fdio.infra.terraform/"
pushd "terraform-aws-fdio-csit-dash-app-base"
export BUILD_ID=43
export TF_VAR_application_version="${BUILD_ID-}"
export TF_LOG=INFO
terraform validate
terraform init
terraform apply -no-color -auto-approve
application_version="$(terraform output application_version)"
popd
popd

#aws --region eu-central-1 elasticbeanstalk update-environment \
#    --environment-name fdio-csit-dash-env \
#    --version-label "${application_version}"
