#!/bin/bash

sudo -H apt-get update
sudo -H apt-get purge -y unscd
sudo -H apt-get install --no-install-recommends -y \
        ca-certificates \
        git \
        make \
        jq \
        nmap \
        curl \
        uuid-runtime

sudo -H chown -R berlin: /opt

sudo -H su -c 'git clone https://git.openstack.org/openstack/openstack-helm-infra /opt/openstack-helm-infra' berlin
sudo -H su -c '(cd /opt/openstack-helm-infra; git reset --hard master)' berlin # replace with locked in commit for workshop
sudo -H su -c '(cd /opt/openstack-helm-infra; make dev-deploy setup-host)' berlin
sudo -H su -c '(cd /opt/openstack-helm-infra; make dev-deploy k8s)' berlin

sudo -H su -c 'git clone https://git.openstack.org/openstack/openstack-helm /opt/openstack-helm' berlin
sudo -H su -c '(cd /opt/openstack-helm; git reset --hard master)' berlin # replace with locked in commit for workshop
sudo -H su -c '(cd /opt/openstack-helm; sudo -H make pull-all-images)' berlin
sudo -H su -c '(cd /opt/openstack-helm-infra; sudo -H make pull-all-images)' berlin
sudo -H docker pull docker.io/openstackhelm/gate-utils:v0.1.0
sudo -H su -c '(cd /opt/openstack-helm-infra; make)' berlin
sudo -H su -c '(cd /opt/openstack-helm; make)' berlin
sudo -H pip install python-openstackclient python-heatclient

sudo -H su -c 'git clone https://github.com/alanmeadows/berlin-workshop.git /opt/berlin-workshop' berlin
sudo -H su -c 'cp -rav /opt/berlin-workshop/armada/* ${HOME}/' berlin
sudo -H su -c 'cp -rav /opt/openstack-helm/tools/deployment/developer/common/170-setup-gateway.sh ${HOME}/' berlin

sudo -H mkdir -p /etc/openstack
sudo -H tee /etc/openstack/clouds.yaml <<EOF
clouds:
  openstack_helm:
    region_name: RegionOne
    identity_api_version: 3
    auth:
      username: 'admin'
      password: 'berlin'
      project_name: 'admin'
      project_domain_name: 'default'
      user_domain_name: 'default'
      auth_url: 'http://keystone.openstack.svc.cluster.local/v3'
EOF
sudo -H chown -R berlin: /etc/openstack
sudo -H su -c 'echo "export OS_CLOUD=openstack_helm" >> /home/berlin/.bashrc' berlin

sudo -H su -c 'curl -L -o /home/berlin/important-file.jpg https://imgflip.com/s/meme/Cute-Cat.jpg' berlin
sudo -H su -c 'cd /home/berlin; ./010-armada-host-setup.sh' berlin
sudo -H su -c 'cd /home/berlin; ./015-armada-build.sh' berlin
sudo -H su -c 'cd /home/berlin; ./020-armada-render-manifests.sh' berlin
sudo -H su -c 'cd /home/berlin; ./025-armada-validate-manifests.sh' berlin
sudo -H su -c 'cd /home/berlin; export MANIFESTS="armada-firstboot" && ./030-armada-apply-manifests.sh' berlin
