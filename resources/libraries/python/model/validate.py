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

"""Module for validating JSON instances against schemas.

Short module currently, as we validate only testcase info outputs.
Structure will probably change when we start validation mode file types.
"""

import json
import jsonschema
import yaml


def get_validators():
    """Return mapping from file types to validator instances.

    Uses hardcoded file types and paths to schemas on disk.

    :returns: Validators, currently just for tc_info_output.
    :rtype: Mapping[str, jsonschema.validators.Validator]
    :raises RuntimeError: If schemas are not readable or not valid.
    """
    relative_path = "docs/model/current/schema/test_case.info.schema.yaml"
    # Robot is always started when CWD is CSIT_DIR.
    with open(relative_path, "rt", encoding="utf-8") as file_in:
        #schema = json.load(file_in)
        schema = json.dumps(yaml.safe_load(file_in.read()))
    validator_class = jsonschema.validators.validator_for(schema)
    validator_class.check_schema(schema)
    fmt_checker = jsonschema.FormatChecker()
    validator = validator_class(schema, format_checker=fmt_checker)

    return dict(tc_info=validator)


def validate(file_path, validator):
    """Load data from disk, use validator to validate it.

    :param file_path: Local filesystem path including the file name to load.
    :param validator: Validator instance to use for validation.
    :type file_path: str
    :type validator: jsonschema.validators.Validator
    :raises RuntimeError: If schema validation fails.
    """
    with open(file_path, "rt", encoding="utf-8") as file_in:
        instance = json.load(file_in)
    error = jsonschema.exceptions.best_match(validator.iter_errors(instance))
    if error is not None:
        raise error
