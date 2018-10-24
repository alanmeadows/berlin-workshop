# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys
import json
import click
import os.path
import sys
import re
import sys
from haikunator import Haikunator
from pkg_resources import load_entry_point
from engine import TemplateGenerator, CloudInit
import deployer

LOG = logging.getLogger(__name__)

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(name)s:%(funcName)s [%(lineno)3d] %(message)s'  # noqa

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '-v',
    '--verbose',
    is_flag=bool,
    default=False,
    help='Enable debug logging')

def main(*, verbose):
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(format=LOG_FORMAT, level=log_level)

@main.command(help='Build Artifacts for Deployment')
@click.option(
    '-n',
    '--node',
    'nodes',
    required=True,
    help='Node Count')
@click.option(
    '-r',
    '--resource-group',
    'resource_group',
    default="azure-test",
    help="Resource Group used to deploy Artifacts")
@click.option(
    '-l',
    '--location',
    'location',
    default="westus",
    help="Azure Region")
@click.option(
    '-f',
    '--first-boot',
    'first_boot_path',
    required=True,
    help="Path to first boot script")
@click.pass_context
def azure(ctx, nodes, resource_group, location, first_boot_path):

    my_subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID', '11111111-1111-1111-1111-111111111111')
    my_resource_group =  resource_group
    my_pub_ssh_key_path = os.path.expanduser('~/.ssh/id_rsa.pub')

    msg = "\nInitializing the Deployer class with subscription id: {}, resource group: {}" \
        "\nand public key located at: {}...\n\n"
    msg = msg.format(my_subscription_id, my_resource_group, my_pub_ssh_key_path)

    print(msg)

    # build template

    cloudinit = CloudInit()
    cloudinit.write_file('/opt/workshop_boot.sh', content=open(first_boot_path, 'r').read())
    cloudinit.runcmd('/opt/workshop_boot.sh')
    cloudinit_data = cloudinit.render()
    tgen = TemplateGenerator()

    # generate password
    password = Haikunator().haikunate()

    # generate deployment template
    template = json.loads(tgen.template_azure(nodes, cloudinit_data, location, password))

    # debug
    # print(template)

    my_deployment = deployer.Deployer(my_subscription_id, my_resource_group, my_pub_ssh_key_path)

    print("Beginning the deployment... \n\n")
    
    # Deploy the template
    my_deployment.deploy(template)

    print("Done deploying!!\n\n")

    for node_num in range(int(nodes)):
        print("ssh -o PreferredAuthentications=password berlin@{}-{}.{}.cloudapp.azure.com using password '{}'".format(my_deployment.dns_label_prefix, str(node_num), location, password))

    user_input = input('Press enter to delete ALL resources.')

    # Destroy the resource group which contains the deployment
    my_deployment.destroy()



if __name__ == '__main__':
    main(obj={})
