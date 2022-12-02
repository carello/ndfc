""" This program executes NDFC APIs to configure: VRFs, networks and deployment """

# to view doc stings run: 'python -m pydoc ./ndfc_build3.py' or 'python -m pydoc -b'

import json
import time
import sys
import os
import logging
import requests
import urllib3

urllib3.disable_warnings(category = urllib3.exceptions.InsecureRequestWarning)

##############################
# *** Set up CONSTANTS ***
##############################
LOGGING_STATUS = True
logging.basicConfig(filename='example.log', format="%(asctime)s - %(message)s",
    encoding='utf-8', level=logging.WARNING)

# Enter credentials and server IP
ND_HOST = "https://10.91.86.229"
USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']
ROOT_API = f"{ND_HOST}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/"

# L3 VRF Variables
VRF_VLAN_NAME = "VRF-522"
VRF_SEGMENT_ID = "50222"
VRF_NAME = "cpVRF-50222"
VRF_VLAN_ID = "2222"
VXLAN_FABRIC = "Demo1"
ASN = "65111"

# L2 VNI Variables
GATEWAY_IPADDRESS = "172.222.222.1/24"
L2_VLAN_ID = "2322"
L2_SEGMENT_ID = "30222"
L2_NETWORK_NAME = "cpNetwork_30222"
####################################
####################################


####################################
# *** Set up switches and ports ***
####################################
leaf_switch_dict = {
    "leaf1": "FDO210518NL",
    "leaf2": "FDO20352B5P"
    }

# The Value must be a type string without any spaces. e.g "SERIAL_NUM: "Ethernetx/y,Ethernetx/z"
switchport_dict = {
    "FDO210518NL": "Ethernet1/6",
    "FDO20352B5P": "Ethernet1/30,Ethernet1/31"
}
####################################
####################################


####################################
# *** Functions ***
####################################
def status_check(resp):
    """ Check request status return code. """

    if resp.status_code != 200:
        print("\nERROR... exiting program.")
        sys.exit()
    else:
        print("--> Success")


def url_ok(uri, head, pay):
    """ Validate URL availability """

    try:
        print("-> Checking URL request...")
        response = requests.request("POST", uri, headers=head, data=pay, verify=False, timeout=3)

    except requests.exceptions.RequestException as err:
        print("Request Exception found, please see logs. Exiting program...")
        if LOGGING_STATUS:
            logging.warning(err)
        sys.exit(1)

    return response


def login():
    """ Login into ND and return a token. """

    url = f"{ND_HOST}/login"

    payload = json.dumps({
        "userName": USER,
        "userPasswd": PASSWORD,
        "domain": "local"
    })
    headers = {'Content-Type': 'application/json'}

    print("-> Logging into Nexus Dashboard...")
    resp = url_ok(url, headers, payload)
    print("-> Success.")

    data = json.loads(resp.text)['token']
    #print(data)

    return data


def create_vrf(token):
    """ Create a new VRF. """

    url = f"{ROOT_API}{VXLAN_FABRIC}/vrfs"

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

    print("\n-> Creating VRF...")
    url_ok(url, headers, payload)
    print("-> Success.")

    #print(resp.text)



def attach_vrf_new(token):
    """ Creating iteration of switch dictionary """

    print("\n-> Attaching VRF...")
    url = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/attachments"
    #print(url)

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    lan_attach_list = []

    for serial in leaf_switch_dict.values():
        # print(serial)
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
        # print("\n", attachment_template)
        lan_attach_list.append(attachment_template)

    #print("\nPrinting lan attach list")
    #print(lan_attach_list)

    attachlist_build = [{
            "vrfName": VRF_NAME,
            "lanAttachList": lan_attach_list
            }]

    #print("\nAttach list build")
    #print(attachlist_build)

    payload = json.dumps(attachlist_build)

    #print("\n", "printing composite build 'NEW PAYLOAD' with json.dumps list")
    #print(type(new_payload))
    #print(new_payload)

    response = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=3)

    print(response.text)
    #status_check(response)


def deploy_vrf(token):
    """ Deploy VRF. """

    print("\n-> Deploying VRF...")
    url = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/deployments"
    #print(url)

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"vrfNames": VRF_NAME})

    response = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=3)

    #print(response.text)
    #status_check(response)


def create_network(token):
    """ Create networks. """

    print("\n-> Creating network...")

    url = f"{ROOT_API}{VXLAN_FABRIC}/networks"
    #print(url)

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

    response = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=3)

    #print(response.text)
    #status_check(response)


def attach_network(token):
    """ Attach network to switches and assing access ports. """

    print("\n-> Attaching network...")

    url = f"{ROOT_API}{VXLAN_FABRIC}/networks/attachments"
    #print(url)

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    vrf_lan_attach_list = []

    for serial in leaf_switch_dict.values():
        if serial in switchport_dict.keys():
            lan_attachment_template = {
                "fabric": VXLAN_FABRIC,
                "networkName": L2_NETWORK_NAME,
                "serialNumber": serial,
                "switchPorts": switchport_dict[serial],
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
            vrf_lan_attach_list.append(lan_attachment_template)

    #print(vrf_lan_attach_list)
    #print()

    attachlist_vrf_lan_build = [{
        "networkName": L2_NETWORK_NAME,
        "lanAttachList": vrf_lan_attach_list
    }]

    #print(attachlist_vrf_lan_build)
    #print()

    payload = json.dumps(attachlist_vrf_lan_build)
    #print(payload)

    response = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=3)

    print(response.text)
    #status_check(response)


def deploy_network(token):
    """ Deploy the networks. """
    print("\n-> Deploying network on interfaces...")

    url = f"{ROOT_API}{VXLAN_FABRIC}/networks/deployments"
    #print(url)

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"networkNames": L2_NETWORK_NAME})

    response = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=3)

    #print(response.text)
    #status_check(response)

####################################
####################################

####################################
# *** Executing Program ***
####################################
def main():
    """ Main section to run functions. """

    tok = login()
    time.sleep(4)

    create_vrf(tok)
    time.sleep(8)

#    attach_vrf_new(tok)
#    time.sleep(10)

#    deploy_vrf(tok)
#    time.sleep(15)

#    create_network(tok)
#    time.sleep(8)

#    attach_network(tok)
#    time.sleep(10)

#    deploy_network(tok)
#    time.sleep(15)


if __name__ == '__main__':
    main()
    print("\nProgram Completed!")
