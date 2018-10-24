import json
import yaml
import os
import base64
from jinja2 import Environment, FileSystemLoader

class TemplateGenerator(object):

    def __init__(self):
        pass

    def template_azure(self, node_count, cloudinit, location, password):
        '''
        Return an azure deployment for the specified nodes
        '''

        # take cloud init data abd b64 encode
        cloudinit_b64 = base64.b64encode(cloudinit.encode('ascii)')).decode('UTF-8')

        env = Environment(loader=FileSystemLoader('templates'))
        template  = env.get_template('deploytemplate.json.j2')

        rendered_template = template.render(
          node_count=int(node_count), cloudinit=cloudinit_b64, location=location, password=password
        )

        return rendered_template

class CloudInit(object):

    def __init__(self):
        '''Initialize the cloud init class'''
        self.yaml = {}
        self.yaml['write_files'] = []
        self.yaml['runcmd'] = []

    def write_file(self, path, content, permissions='0755', owner='root:root', encoding=None):
        '''Write fules helper'''

        yamlblurb = {

          'encoding': encoding,
          'content': content,
          'owner': owner,
          'permissions': permissions,
          'content': content,
          'path': path

        }

        # remove null encodings
        if not encoding:
            del yamlblurb['encoding']

        self.yaml['write_files'].append(yamlblurb)

    def runcmd(self, cmd):
        '''cmd can be a string or a list'''
        self.yaml['runcmd'].append(cmd)

    def render(self):
        '''Render cloud init object as yaml'''
        return "#cloud-config\n%s" % yaml.dump(self.yaml)