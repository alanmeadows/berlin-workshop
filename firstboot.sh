#!/bin/bash

sudo -H apt-get update
sudo -H apt-get install -y git jq nmap

sudo -H chown -R berlin: /opt

sudo -H su -c 'git clone https://git.openstack.org/openstack/openstack-helm-infra /opt/openstack-helm-infra' berlin
sudo -H su -c '(cd /opt/openstack-helm-infra; git reset --hard master)' berlin # replace with locked in commit for workshop
sudo -H su -c '/opt/openstack-helm-infra/tools/gate/devel/start.sh' berlin

sudo -H su -c 'git clone https://git.openstack.org/openstack/openstack-helm /opt/openstack-helm' berlin
sudo -H su -c '(cd /opt/openstack-helm; git reset --hard master)' berlin # replace with locked in commit for workshop
sudo -H su -c '(cd /opt/openstack-helm; sudo -H make pull-all-images)' berlin
sudo -H su -c '(cd /opt/openstack-helm; kubectl replace -f ./tools/kubeadm-aio/assets/opt/rbac/dev.yaml)' berlin
sudo -H su -c '(cd /opt/openstack-helm; make)' berlin
sudo -H pip install python-openstackclient python-heatclient

sudo -H su -c 'git clone https://github.com/alanmeadow/berlin-workshop.git /opt/berlin-workshop' berlin
sudo -H su -c 'cp -rav /opt/berlin-workshop/armada/* ${HOME}/' berlin

sudo -H mkdir -p /etc/openstack
cat << EOF | sudo -H tee -a /etc/openstack/clouds.yaml
clouds:
  openstack_helm:
    region_name: RegionOne
    identity_api_version: 3
    auth:
      username: 'admin'
      password: 'password'
      project_name: 'admin'
      project_domain_name: 'default'
      user_domain_name: 'default'
      auth_url: 'http://keystone.openstack.svc.cluster.local/v3'
EOF
sudo -H chown -R berlin: /etc/openstack

sudo -H su -c 'curl -L -o /home/berlin/important-file.jpg https://imgflip.com/s/meme/Cute-Cat.jpg' berlin
