""" A module docstring placeholder """

# working on loops for switch attachments

import json
import time
import sys
import os
import requests
import urllib3

#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(category = urllib3.exceptions.InsecureRequestWarning)

# Enter credentials and server IP
ND_SERVER = "10.91.86.229"
USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']

#########################
# L3 VRF Variable
VRF_VLAN_NAME = "VRF-522"
VRF_SEGMENT_ID = "50222"
VRF_NAME = "cpVRF-50222"
VRF_VLAN_ID = "2222"
VXLAN_FABRIC = "Demo1"

# I think this is redundant and could be deleted
#VRF_VLAN = "2222"

ASN = "65111"

##########################
# L2 VNI Variables, a better naming convention and organization is needed
SWITCH1 = "FDO210518NL"
SWITCH2 = "FDO20352B5P"
switch_dict = {
    "leaf1": "FDO210518NL",
    "leaf2": "FDO20352B5P"
    }

GATEWAY_IPADDRESS = "172.222.222.1/24"
L2_VLAN_ID = "2322"
L2_SEGMENT_ID = "30222"
L2_NETWORK_NAME = "cpNetwork_30222"
SWITCH1_SWITCHPORTS = "Ethernet1/26"
SWITCH2_SWITCHPORTS = "Ethernet1/26"


def status_check(resp):
    """ A doc string. """
    if resp.status_code != 200:
        print("Error...")
        sys.exit()


def login():
    """ A doc string. """
    print("Logging into Nexus Dashboard...")
    url = f"https://{ND_SERVER}/login"

    payload = json.dumps({
        "userName": USER,
        "userPasswd": PASSWORD,
        "domain": "local"
    })
    headers = {'Content-Type': 'application/json'}

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False, timeout=3)
    data = json.loads(response.text)['token']

    #print(data)
    return data


def create_vrf(token):
    """ A doc string. """
    print("\nCreating VRF...")
    url = f"https://{ND_SERVER}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{VXLAN_FABRIC}/vrfs"

    vrf_temp_cfg = {
        "advertiseDefaultRouteFlag": True,
        "routeTargetImport": "",
        "vrfVlanId": VRF_VLAN_ID,
        "isRPExternal": False,
        "vrfDescription": "",
        "disableRtAuto": False,
        "L3VniMcastGroup": "",
        "maxBgpPaths": "1",
        "maxIbgpPaths": "2",
        "vrfSegmentId": VRF_SEGMENT_ID,
        "routeTargetExport": "",
        "ipv6LinkLocalFlag": True,
        "vrfRouteMap": "FABRIC-RMAP-REDIST-SUBNET",
        "routeTargetExportMvpn": "",
        "ENABLE_NETFLOW": False,
        "configureStaticDefaultRouteFlag": True,
        "tag": "12345",
        "rpAddress": "",
        "trmBGWMSiteEnabled": False,
        "nveId": "1",
        "routeTargetExportEvpn": "",
        "NETFLOW_MONITOR": "",
        "bgpPasswordKeyType": "3",
        "bgpPassword": "",
        "mtu": "9216",
        "multicastGroup": "",
        "routeTargetImportMvpn": "",
        "isRPAbsent": False,
        "advertiseHostRouteFlag": False,
        "vrfVlanName": "",
        "trmEnabled": False,
        "loopbackNumber": "",
        "asn": ASN,
        "vrfIntfDescription": "",
        "routeTargetImportEvpn": "",
        "vrfName": VRF_NAME
        }


    payload = json.dumps({
        "fabric": VXLAN_FABRIC,
        "vrfName": VRF_NAME,
        "vrfTemplate": "Default_VRF_Universal",
        "vrfExtensionTemplate": "Default_VRF_Extension_Universal",
        "vrfTemplateConfig": str(vrf_temp_cfg),
        "tenantName": None,
        "vrfId": VRF_SEGMENT_ID,
        "serviceVrfTemplate": None,
        "source": None,
        "hierarchicalKey": VXLAN_FABRIC
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': str(token)
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False, timeout=3)

    print(response.text)
    status_check(response)


# Experimenting with iteration over switch dict
def get_switch_serial():
    """ Creating iteration of switch dictionary """

    lan_attach_list = []

    for switch, serial in switch_dict.items():
        print(switch, serial)
        attachment_template = {
            "fabric": VXLAN_FABRIC,
            "vrfName": VRF_NAME,
            "serialNumber": serial,
            "vlan": VRF_VLAN_ID,
            "freeformConfig": "",
            "deployment": True,
            "extensionValues": "",
            "instanceValues": "{\"loopbackId\":\"\",\"loopbackIpAddress\":\"\",\"loopbackIpV6Address\":\"\"}"
        }
        #print("\n", attachment_template)
        lan_attach_list.append(attachment_template)


    attachlist_build = [
        {
            "vrfName": VRF_NAME,
            "lanAttachList": [lan_attach_list]
        }
        ]


    new_payload = json.dumps(attachlist_build)
    print("\n", "printing composite build 'NEW PAYLOAD' of list")
    print(type(new_payload))
    print("\n", new_payload)



def attach_vrf(token):
    """ A doc string. """
    print("\nAttaching VRF...")
    url = f"https://{ND_SERVER}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{VXLAN_FABRIC}/vrfs/attachments"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps([
        {
            "vrfName": VRF_NAME,
            "lanAttachList": [
        {
            "fabric": VXLAN_FABRIC,
            "vrfName": VRF_NAME,
            "serialNumber": SWITCH1,
            "vlan": VRF_VLAN_ID,
            "freeformConfig": "",
            "deployment": True,
            "extensionValues": "",
            "instanceValues": "{\"loopbackId\":\"\",\"loopbackIpAddress\":\"\",\"loopbackIpV6Address\":\"\"}"
        },
        {
            "fabric": VXLAN_FABRIC,
            "vrfName": VRF_NAME,
            "serialNumber": SWITCH2,
            "vlan": VRF_VLAN_ID,
            "freeformConfig": "",
            "deployment": True,
            "extensionValues": "",
            "instanceValues": "{\"loopbackId\":\"\",\"loopbackIpAddress\":\"\",\"loopbackIpV6Address\":\"\"}"
        }
        ]
    }
    ])

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False, timeout=3)

    print(response.text)
    status_check(response)


def deploy_vrf(token):
    """ A doc string. """
    print("\nDeploying VRF...")
    url = f"https://{ND_SERVER}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{VXLAN_FABRIC}/vrfs/deployments"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"vrfNames": VRF_NAME})

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False, timeout=3)

    print(response)
    status_check(response)


def create_network(token):
    """ A doc string. """
    print("\nCreating network...")

    url = f"https://{ND_SERVER}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{VXLAN_FABRIC}/networks"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    network_template_cfg = {"gatewayIpAddress": GATEWAY_IPADDRESS,
                            "gatewayIpV6Address": "",
                            "vlanName": "",
                            "intfDescription": "",
                            "mtu": "",
                            "secondaryGW1": "",
                            "secondaryGW2": "",
                            "suppressArp": "false",
                            "enableIR": "false",
                            "trmEnabled": "false",
                            "rtBothAuto": "false",
                            "enableL3OnBorder": "false",
                            "mcastGroup": "239.1.1.0",
                            "dhcpServerAddr1": "",
                            "dhcpServerAddr2": "",
                            "vrfDhcp": "",
                            "loopbackId": "",
                            "tag": "12345",
                            "vrfName": VRF_NAME,
                            "isLayer2Only": "false",
                            "nveId": 1,
                            "vlanId": L2_VLAN_ID,
                            "segmentId": L2_SEGMENT_ID,
                            "networkName": L2_NETWORK_NAME
                            }

    payload = json.dumps({
        "fabric": VXLAN_FABRIC,
        "vrf": VRF_NAME,
        "networkName": L2_NETWORK_NAME,
        "displayName": L2_NETWORK_NAME,
        "networkId": L2_SEGMENT_ID,
        "networkTemplateConfig": str(network_template_cfg),
        "networkTemplate": "Default_Network_Universal",
        "networkExtensionTemplate": "Default_Network_Extension_Universal",
        "source": None,
        "serviceNetworkTemplate": None,
        "interfaceGroups": None,
        "hierarchicalKey": None
    })

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False, timeout=3)

    print(response.text)
    status_check(response)

def attach_network(token):
    """ A doc string. """
    print("\nAttaching network...")

    url = f"https://{ND_SERVER}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{VXLAN_FABRIC}/networks/attachments"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps([
        {
            "networkName": L2_NETWORK_NAME,
            "lanAttachList": [
                {
                    "fabric": VXLAN_FABRIC,
                    "networkName": L2_NETWORK_NAME,
                    "serialNumber": SWITCH1,
                    "switchPorts": SWITCH1_SWITCHPORTS,
                    "detachSwitchPorts": "",
                    "vlan": L2_VLAN_ID,
                    "dot1QVlan": 1,
                    "untagged": False,
                    "freeformConfig": "",
                    "deployment": True,
                    "toPorts": "",
                    "extensionValues": "",
                    "instanceValues": ""
                },
                {
                    "fabric": VXLAN_FABRIC,
                    "networkName": L2_NETWORK_NAME,
                    "serialNumber": SWITCH2,
                    "switchPorts": SWITCH2_SWITCHPORTS,
                    "detachSwitchPorts": "",
                    "vlan": L2_VLAN_ID,
                    "dot1QVlan": 1,
                    "untagged": False,
                    "freeformConfig": "",
                    "deployment": True,
                    "toPorts": "",
                    "extensionValues": "",
                    "instanceValues": ""
                }
            ]
        }
    ])

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False, timeout=3)

    print(response.text)
    status_check(response)


def deploy_network(token):
    """ A doc string. """
    print("\nDeploying network on interfaces...")

    url = f"https://{ND_SERVER}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{VXLAN_FABRIC}/networks/deployments"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"networkNames": L2_NETWORK_NAME})

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False, timeout=3)

    print(response.text)
    status_check(response)


def main():
    """ A doc string. """


    tok = login()
 #   time.sleep(4)

    get_switch_serial()


    '''
    create_vrf(tok)
    time.sleep(8)

    attach_vrf(tok)
    time.sleep(10)

    deploy_vrf(tok)
    time.sleep(15)
    # Need longer wait time after deploy (10sec)

    create_network(tok)
    time.sleep(8)

    attach_network(tok)
    time.sleep(10)

    deploy_network(tok)
    time.sleep(15)
    # Need longer wait time after deploy (10sec)
    '''

if __name__ == '__main__':
    main()
    print("\nTadah!!!")
