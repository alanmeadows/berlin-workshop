"""A deployer class to deploy a template on Azure"""
import os.path
import json
import uuid
from haikunator import Haikunator
from azure.storage.blob import BlockBlobService, PublicAccess
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode

class Deployer(object):
    """ Initialize the deployer class with subscription, resource group and public key.

    :raises IOError: If the public key path cannot be read (access or not exists)
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """
    name_generator = Haikunator()

    def __init__(self, subscription_id, resource_group, pub_ssh_key_path='~/.ssh/id_rsa.pub'):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.dns_label_prefix = self.name_generator.haikunate()

        pub_ssh_key_path = os.path.expanduser(pub_ssh_key_path)
        # Will raise if file not exists or not enough permission
        with open(pub_ssh_key_path, 'r') as pub_ssh_file_fd:
            self.pub_ssh_key = pub_ssh_file_fd.read()

        self.credentials = ServicePrincipalCredentials(
            client_id=os.environ['AZURE_CLIENT_ID'],
            secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant=os.environ['AZURE_TENANT_ID']
        )
        self.client = ResourceManagementClient(self.credentials, self.subscription_id)

        self.blob_service_account_name = os.environ.get('AZURE_BLOB_ACCOUNT_NAME', '')
        self.blob_service_account_key  = os.environ.get('AZURE_BLOB_ACCOUNT_KEY', '')

    def upload(self, container_name, file_path, public=False,):
        """Upload a file, return a URL to access it"""

        print("Using account=%s, key=%s" % (self.blob_service_account_name, self.blob_service_account_key))
        blob_service = BlockBlobService(account_name=self.blob_service_account_name, account_key=self.blob_service_account_key)

        blob_service.create_container(container_name)

        if public:
            blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

        randomizer = str(uuid.uuid4())[0:8]
        myblobname = randomizer + '-' + os.path.basename(file_path)

        print("Creating blob=%s from file=%s in container=%s" % (myblobname, file_path, container_name))
        blob_service.create_blob_from_path(container_name, myblobname, file_path)

        return blob_service.make_blob_url(container_name, myblobname, protocol=None, sas_token=None)

    def deploy(self, template, location='westus'):
        """Deploy the template to a resource group."""
        self.client.resource_groups.create_or_update(
            self.resource_group,
            {
                'location':location
            }
        )

        # template_path = os.path.join(os.path.dirname(__file__), 'templates', 'template.json')
        # with open(template_path, 'r') as template_file_fd:
        #     template = json.load(template_file_fd)

        parameters = {
            'sshKeyData': self.pub_ssh_key,
            'dnsLabelPrefix': self.dns_label_prefix,
        }
        parameters = {k: {'value': v} for k, v in parameters.items()}

        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters
        }

        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group,
            'berlin-workshop',
            deployment_properties
        )
        deployment_async_operation.wait()

    def destroy(self):
        """Destroy the given resource group"""
        self.client.resource_groups.delete(self.resource_group)
