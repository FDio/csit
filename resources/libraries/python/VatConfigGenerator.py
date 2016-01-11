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

"""Can be used to generate VAT scripts from VAT template files."""

from robot.api import logger


class VatConfigGenerator(object):
    """Generates VAT configuration scripts from VAT script template files.
    """
    def __init__(self):
        pass

    @staticmethod
    def generate_vat_config_file(template_file, env_var_dict, out_file):
        """ Write VAT configuration script to out file.

        Generates VAT configuration script from template using
        dictionary containing environment variables
        :param template_file: file that contains the VAT script template
        :param env_var_dict: python dictionary that maps test
        environment variables
        """

        template_data = open(template_file).read()
        logger.trace("Loaded template file: \n '{0}'".format(template_data))
        generated_config = template_data.format(**env_var_dict)
        logger.trace("Generated script file: \n '{0}'".format(generated_config))
        with open(out_file, 'w') as work_file:
            work_file.write(generated_config)

    @staticmethod
    def generate_vat_config_string(template_file, env_var_dict):
        """ Return wat config string generated from template.

        Generates VAT configuration script from template using
        dictionary containing environment variables
        :param template_file: file that contains the VAT script template
        :param env_var_dict: python dictionary that maps test
        environment variables
        """

        template_data = open(template_file).read()
        logger.trace("Loaded template file: \n '{0}'".format(template_data))
        generated_config = template_data.format(**env_var_dict)
        logger.trace("Generated script file: \n '{0}'".format(generated_config))
        return generated_config
