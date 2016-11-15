#!/bin/sh

# Copyright (c) 2016 Cisco and/or its affiliates.
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
exit 0

if [ "$1" = "" ]
then
  echo "Syntax: $0 <path to image file>"
  echo 
  echo "Environment variables that are required:"
  echo " VIRL_USER, VIRL_PASSWORD - VIRL username and password"
  echo " VIRL_IMAGE_SUBTYPE       - Image subtype to use (most likely 'server')"
  echo " VIRL_IMAGE_NAME          - The intended name for the image in VIRL"
  exit 1
fi

VIRL_IMAGE_FILE=$1

if [ "$VIRL_USER" = "" ] || [ "$VIRL_PASSWORD" = "" ]
then
  echo "VIRL user or password not defined, not uploading image to VIRL."
  echo "Define VIRL_USER and VIRL_PASSWORD environment variables if image upload"
  echo "to VIRL is intended."
  exit 0
fi

if [ "$VIRL_IMAGE_SUBTYPE" = "" ] || [ "$VIRL_IMAGE_NAME" = "" ]
then
  echo "VIRL_IMAGE_SUBTYPE, VIRL_IMAGE_NAME must both be defined"
  echo "variables must all be set."
  exit 1
fi

if [ ! -f $VIRL_IMAGE_FILE ]
then
  echo "VIRL image file $VIRL_IMAGE_FILE not found"
  exit 1
fi

echo Uploading file $VIRL_IMAGE_FILE to VIRL
echo as $VIRL_IMAGE_NAME

export VIRL_IMAGE_NAME

existing_image_id=$(virl_uwm_client --quiet -u ${VIRL_USER} -p ${VIRL_PASSWORD} \
  image-info | \
  grep -E "^              u'name'|^              u'id'" | \
  grep -B 1 "u'${VIRL_IMAGE_SUBTYPE}-${VIRL_IMAGE_NAME}'" | \
  grep -E "^              u'id'" | \
  cut -f 4 -d "'")

if [ "${existing_image_id}" = "" ]
then
  echo Image does not exist yet
else
  echo Image exists with ID $existing_image_id
  virl_uwm_client --quiet -u ${VIRL_USER} -p ${VIRL_PASSWORD} image-delete \
    --id ${existing_image_id}
fi

virl_uwm_client -u ${VIRL_USER} -p ${VIRL_PASSWORD} image-create --subtype ${VIRL_IMAGE_SUBTYPE} --version ${VIRL_IMAGE_NAME} --image-on-server ${VIRL_IMAGE_FILE}
