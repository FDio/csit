#!/usr/bin/env bash

set -euo pipefail

tagged_img_ids="$(docker images | grep 'fdiotools/builder' | mawk '/prod|sand|test/{print $3}' | uniq)"
if [ -z "${tagged_img_ids-}" ] ; then
    echo "No tagged 'fdiotools/builder' images found on $(hostname)!" >&2
    exit 1
fi

for img_id in $(docker images | grep 'fdiotools/builder' | mawk '{print $3}' | uniq) ; do
    if ! echo "$img_id" | grep -q "$tagged_img_ids" ; then
        purge_tag="$(docker image inspect "$img_id" | jq '.[].RepoTags[]')"
        echo -e "Removing docker image "$img_id": "$purge_tag""
        sudo docker rmi "$img_id"
    fi
done
