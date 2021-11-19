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

docker build \
    --tag glue:3.0.0 .

docker run \
    --rm \
    --interactive \
    --tty \
    --detach \
    --publish 4040:4040 \
    --volume $HOME/.aws:/root/.aws \
    --volume $PWD:/app \
    --name glue \
    glue:3.0.0

docker exec \
    --interactive \
    --tty \
    glue \
    gluesparksubmit \
        --master local \
        --deploy-mode client \
        --name trending_s3 \
        job_trending_s3.py

docker exec \
    --interactive \
    --tty \
    glue \
    gluesparksubmit \
        --master local \
        --deploy-mode client \
        --name stats_s3 \
        job_stats_s3.py

docker stop \
    --name glue
