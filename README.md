# ocp-pulumi
Pulimi's Infrastructure as Code.

# Create a VPN connection to Azure VNET

This example deploys VPN connection to Azure VNET and create a VM to use it as Local Container Registry. 

## Prerequisites

1. [Install Pulumi](https://www.pulumi.com/docs/get-started/install/)
1. [Configure Pulumi for Azure](https://www.pulumi.com/docs/intro/cloud-providers/azure/setup/)
1. [Configure Pulumi for Python](https://www.pulumi.com/docs/intro/languages/python/)

## Deploying and running the program

1. Set up a virtual Python environment and install dependencies

    ```bash
    $ virtualenv -p python3 venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    ```

1. Create a new stack:

    ```bash
    $ git clone https://github.com/dwojciec/ocp-pulumi.git && cd ocp-pulumi
    $ pulumi stack init dev
    ```

1. Set the Azure environment:

    ```bash
    $ vi Pulumi.dev.yaml 
    ```

and update the file with all this values :


```bash
    config:
  azure:environment: public
  azure:location: centralus
  ocp-pulumi:address_space: 175.16.200.0/26
  ocp-pulumi:gateway_address_spaces: 10.0.1.0/24
  ocp-pulumi:public_certificate_data: MIIDtjCCAp4CCQCiaAT3f6TgIjANBgkqhkiG9w0BAQUFADCBnDELMAkGA1UEBhMCRlIxEDAOBgNVBAgMB0hlcmF1bHQxEDAOBgNVBAcMB0dyYWJlbHMxDzANBgNVBAoMBlJlZEhhdDELMAkGA1UECwwCSVQxHDAaBgNVBAMME2hybWNkZW1vLnJlZGhhdC5jb20xLTArBgkqhkiG9w0BCQEWHmRpZGllci53b2pjaWVjaG93c2tpQGdtYWlsLmNvbTAeFw0xOTExMjYxMzI5NTRaFw0yOTExMjMxMzI5NTRaMIGcMQswCQYDVQQGEwJGUjEQMA.......
  ocp-pulumi:rhcos_storage_name: pulumistorage
  ocp-pulumi:root_certificates: hrmcdemo.redhat.com
  ocp-pulumi:ssh_public_key: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCiOIB0PTSuI8Sdes/ExSakdjPiqly54rfD3KN/5jNgVJ7y+WQv24oa6gQjU5qeT0NeWdjP9ZRJ/1KYt6sofZSwHKpaHq9R6xNjiFJdiymWF7sYfN/LWD0VwFyFIHEuo8SpsENHbw43g...........
  ocp-pulumi:subnet_address_spaces: 10.0.0.0/24
  ocp-pulumi:vhd_name: rhcos-42.80.20191002.0.vhd
  ocp-pulumi:vnet_address_spaces: 10.0.0.0/16
  repository:adminPassword: Password123
  repository:adminUser: dwojciec
```

1. Run `pulumi up` to preview and deploy the changes:

    ```
    $ pulumi update
    Previewing update (dev):

     Type                                    Name            Plan
     pulumi:pulumi:Stack                     ocp-pulumi-dev
 +   ├─ azure:core:ResourceGroup             rhcos_images    create
 +   ├─ azure:core:ResourceGroup             common-ocp      create
 +   ├─ azure:network:VirtualNetwork         company-vnet    create
 +   ├─ azure:network:PublicIp               Vnet01GWPIP     create
 +   ├─ azure:storage:Account                pulumistorage   create
 +   ├─ azure:network:PublicIp               server-ip       create
 +   ├─ azure:storage:Container              vhd             create
 +   ├─ azure:network:Subnet                 registry        create
 +   ├─ azure:network:Subnet                 GatewaySubnet   create
 +   ├─ azure:storage:Blob                   copyblob        create
 +   ├─ azure:network:VirtualNetworkGateway  Vnet01GW        create
 +   ├─ azure:network:NetworkInterface       server-nic      create
 +   └─ azure:compute:VirtualMachine         server-vm       create

Outputs:
  + primary_account_key      : output<string>
  + primary_connection_string: output<string>

Resources:
    + 13 to create
    1 unchanged

Do you want to perform this update?
  yes
> no
  details
```

1. Destroy the stack:

    ```
    ▶ pulumi destroy --yes
    Previewing destroy (dev):
    ```

* **[Examples](https://github.com/pulumi/examples)**: browse a number of useful examples across many languages,
  clouds, and scenarios including containers, serverless, and infrastructure.

* **[Reference Docs](https://www.pulumi.com/docs/reference/)**: read conceptual documentation, in addition to details on how
  to configure Pulumi to deploy into your AWS, Azure, or Google Cloud accounts, and/or Kubernetes cluster.

* **[Community Slack](https://slack.pulumi.com)**: join us over at our community Slack channel.  Any and all
  discussion or questions are welcome.