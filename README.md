README

Set Authentication
==================

Create an azurerc file

```
$ cat azurerc 
export AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export AZURE_CLIENT_SECRET=somesupersecret
export AZURE_SUBSCRIPTION_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx



```

Run the application
===================

The firstboot script included in this repository is an example.  It will touch a file `/first-boot-script-ran` to demonstrate it can run.

To launch a single node (`-n 1`) in resource group `azure-test` within location `west-us` and have the VM run the local file `./firstboot.sh` as its first boot script, launch the following:

```
$ python3 ./cli.py azure -n 1 -r azure-test -l westus -f ./firstboot.sh 

Initializing the Deployer class with subscription id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, resource group: azure-test
and public key located at: /home/user/.ssh/id_rsa.pub...

Beginning the deployment... 

Done deploying!!

ssh -o PreferredAuthentications=password berlin@hidden-night-9579-0.westus.cloudapp.azure.com using password 'fragrant-fire-0492'

Press enter to delete ALL resources.
```

