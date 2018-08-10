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

set -exuo pipefail

function get_test_tag_string () {

    set -exuo pipefail

    # Variables read:
    # - GERRIT_EVENT_TYPE - Event type set by gerrit, can be unset.
    # - GERRIT_EVENT_COMMENT_TEXT - Comment text, read for "comment-added" type.
    # Variables set:
    # - TEST_TAG_STRING - The string following "perftest" in gerrit comment, or empty.

    # TODO: ci-management scripts no longer need to perform this.

    trigger=""
    if [[ "${GERRIT_EVENT_TYPE-}" == "comment-added" ]]; then
        # On parsing error, ${trigger} stays empty.
        trigger=$(echo "${GERRIT_EVENT_COMMENT_TEXT}" \
            | grep -oE '(perftest$|perftest[[:space:]].+$)') || true
    fi
    # Set test tags as string.
    TEST_TAG_STRING="${trigger#$"perftest"}"
}
