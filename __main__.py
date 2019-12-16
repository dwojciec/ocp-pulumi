import pulumi
from pulumi import Config, export, ResourceOptions
from pulumi_azure import core, storage, network, lb, compute
import pulumi_random as random


config = pulumi.Config("ocp-pulumi")
root_certificates = config.get("root_certificates") 
public_certificate_data = config.get("public_certificate_data")
address_space = config.get("address_space")
vnet_address_spaces = config.get("vnet_address_spaces")
subnet_address_spaces = config.get("subnet_address_spaces")
vhd_name = config.get("vhd_name")
rhcos_storage_name = config.get("rhcos_storage_name")
gateway_address_spaces = config.get("gateway_address_spaces")
ssh_public_key = config.get("ssh_public_key")

config = pulumi.Config("repository")
admin_user = config.require("adminUser")
admin_password = config.require("adminPassword")

# Create an Azure Resource Group
resource_group = core.ResourceGroup('common-ocp', name='common-ocp')

# Create an Azure network 
vnet = network.VirtualNetwork(
    "company-vnet",
    name="company-vnet",
    resource_group_name=resource_group.name,
    address_spaces=[vnet_address_spaces])

# Create an Azure subnet 
subnet = network.Subnet(
    "registry",
    resource_group_name=resource_group.name,
    address_prefix=subnet_address_spaces,
    virtual_network_name=vnet.name,
    name="registry",
    enforce_private_link_endpoint_network_policies="false")


# Create an Azure subnet
gatewaysubnet = network.Subnet(
    "GatewaySubnet",
    resource_group_name=resource_group.name,
    address_prefix=gateway_address_spaces,
    virtual_network_name=vnet.name,
    name="GatewaySubnet"
    )


# Create an Azure network public-ip 

public_ip = network.PublicIp(
    "Vnet01GWPIP",
    resource_group_name=resource_group.name,
    allocation_method="Dynamic",
    ip_version="IPv4",
    sku="Basic",
    name="Vnet01GWPIP")

# Create an Azure gateway
gateway = network.VirtualNetworkGateway(
    "Vnet01GW",
    name="Vnet01GW",
    resource_group_name=resource_group.name,
    vpn_type="RouteBased", 
    sku="VpnGw1",
    type="Vpn",
    ip_configurations=[{
        "publicIpAddressId": public_ip.id,
        "name": "Vnet01GWPIP",
        "subnet_id": gatewaysubnet.id
    }],
    vpn_client_configuration={
        "rootCertificates": [{
            "name": root_certificates, 
            "publicCertData": public_certificate_data
            }],
        "vpnClientProtocols": ["IkeV2"],
        "address_spaces": [address_space]
        }
)
# preparation of the RHCOS image
# Create an Azure Storage Account
storageaccount = storage.Account("pulumistorage",
                          name=rhcos_storage_name,
                          resource_group_name=resource_group.name,
                          account_kind = 'StorageV2',
                          account_tier='Standard',
                          access_tier='Hot',
                          account_replication_type= 'LRS'
                          )

export('primary_connection_string', storageaccount.primary_connection_string)
export('primary_account_key', storageaccount.primary_access_key)
# Create an Azure storage container

storagecontainer = storage.Container("vhd",
                                  name="vhd",
                                  storage_account_name=storageaccount.name
                                )

# Create an Azure group 
resource_group_images = core.ResourceGroup('rhcos_images', name='rhcos_images')
vhd_name_link = "https://rhcos.blob.core.windows.net/imagebucket/" + vhd_name

# Get Azure copy RHCOS image  
blob_copy = storage.Blob("copyblob", 
                          name=vhd_name,
                          type="Block",
                          source_uri=vhd_name_link,
                          storage_account_name=storageaccount.name,
                          storage_container_name=storagecontainer.name
                         )

server_public_ip = network.PublicIp(
    "server-ip",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    allocation_method="Dynamic")

network_iface = network.NetworkInterface(
    "server-nic",
    resource_group_name=resource_group.name,
    ip_configurations=[{
        "name": "registryVNIC",
        "subnet_id": subnet.id,
        "private_ip_address_allocation": "Dynamic",
        "public_ip_address_id": server_public_ip.id,
    }])

# create a Centos image - we will use it as registry mirror
vm = compute.VirtualMachine(
    "server-vm",
    name="mirror",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    network_interface_ids=[network_iface.id],
    vm_size="Standard_DS1_v2",
    delete_data_disks_on_termination=True,
    delete_os_disk_on_termination=True,
    os_profile={
        "computerName": "hostname",
        "adminUsername": admin_user,
        "adminPassword": admin_password
    },
    os_profile_linux_config={
        "disablePasswordAuthentication": "true",
        "sshKeys" : [{
            "path" : "/home/dwojciec/.ssh/authorized_keys",
            "key_data" :  ssh_public_key
        }]
    },
    storage_os_disk={
        "create_option": "FromImage",
        "name": "mirror_disk"
    },
    storage_image_reference={
        "publisher": "OpenLogic",
        "offer": "CentOS",
        "sku": "7.5",
        "version": "latest"
    })
