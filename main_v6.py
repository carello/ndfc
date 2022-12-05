""" This program executes NDFC APIs to configure: VRFs, networks and deployment """

# to view doc stings run: 'python -m pydoc ./ndfc_build3.py' or 'python -m pydoc -b'
# Nest step: add in request method GET or POST etc... to 'def url_ok'

import json
import time
import sys
import os
import logging
import requests
import urllib3
from data import dbcontent

urllib3.disable_warnings(category = urllib3.exceptions.InsecureRequestWarning)

##############################
# *** Set up CONSTANTS ***
##############################
LOGGING_STATUS = True
logging.basicConfig(filename='ndfc.log', format="%(asctime)s - %(message)s",
    encoding='utf-8', level=logging.DEBUG)

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


#####################################################
# *** Set up switches and ports ***
# Deprecate this and use data/dbcontent.py instead
#####################################################
#leaf_switch_dict = {
#    "leaf1": "FDO210518NL",
#    "leaf2": "FDO20352B5P"
#    }

# The Value must be a type string without any spaces. e.g "SERIAL_NUM: "Ethernetx/y,Ethernetx/z"
#switchport_dict = {
#    "FDO210518NL": "Ethernet1/20",
#    "FDO20352B5P": "Ethernet1/20,Ethernet1/21"
#}
####################################
####################################


####################################
# *** Functions ***
####################################
def url_ok(uri, head, pay, request_method):
    """ Validate URL availability """

    try:
        print("-> Checking URL request...")
        response = requests.request(request_method, uri, headers=head, data=pay, verify=False, timeout=4)
        response.raise_for_status()

    except requests.exceptions.RequestException as err:
        print("Request Exception found, please see logs. Exiting program...")
        if LOGGING_STATUS:
            logging.debug(err)
        sys.exit(1)

        # This will raise an error on STDOUT and exit
        #raise SystemExit(err)

    return response


def check_response_code(resp_code, whereami):
    """ Check response code """

    if resp_code != 200:
        print("Something went wrong, invalid. Please check logs.")
        logging.debug("Returned response code: %s from calling function: %s", resp_code, whereami)
        sys.exit(1)


def check_validity(resp_text):
    """ Check if api execution is proper, 'SUCCESS' """

    for item, output in resp_text.items():
        check_result = output
        if check_result.find("SUCCESS") == -1:
            print("Something went wrong, invalid. Please check logs.")
            out = item, output
            logging.debug(out)
            sys.exit(1)


def login():
    """ Login into ND and return a token. """

    url = f"{ND_HOST}/login"

    payload = json.dumps({
        "userName": USER,
        "userPasswd": PASSWORD,
        "domain": "local"
    })
    headers = {'Content-Type': 'application/json'}

    print("\n-> Logging into Nexus Dashboard...")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, whereami=login.__name__)

    print("-> Success.")

    data = json.loads(resp.text)['token']

    return data

def check_vrf_network_existance(vrf_net, token):
    """ Check if VRF or Network exists """

    headers = {
        'Content-Type': 'application/json',
        'Authorization': str(token)
    }

    payload = {}
    print()
    # This won't work because if code isn't 200, it exits program.
    # We want to only validate code and continue.
    #resp = url_ok(vrf_net, headers, payload, request_method="GET")

    # So in this case, we'll need to send this instead. Rudimentary, could use more error checking.
    resp = requests.request("GET", vrf_net, headers=headers, data=payload, verify=False, timeout=4)

    return resp.status_code


def create_vrf(token):
    """ Create a new VRF. """

    # Check if vrf exists. If so, exit this function, else continue
    vrf = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/{VRF_NAME}"


    resp_vrf_existance = check_vrf_network_existance(vrf, token)

    if resp_vrf_existance == 200:
        print("-> VRF exists. Moving onto next step. ")

    if resp_vrf_existance != 200:
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
        resp = url_ok(url, headers, payload, request_method="POST")
        check_response_code(resp.status_code, create_vrf.__name__)

        print("-> Success.")


def attach_vrf_new(token):
    """ Creating iteration of switch dictionary """

    url = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/attachments"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    # Get device and serial dictionary from data/dbcontent.py
    dev_serial_result = dbcontent.dev_serial(dbcontent.master_list)

    lan_attach_list = []

    for serial in dev_serial_result.values():
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

        lan_attach_list.append(attachment_template)

    attachlist_build = [{
            "vrfName": VRF_NAME,
            "lanAttachList": lan_attach_list
            }]

    payload = json.dumps(attachlist_build)

    print("\n-> Attaching VRF...")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, attach_vrf_new.__name__)

    print("-> Success.")


def deploy_vrf(token):
    """ Deploy VRF. """

    url = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/deployments"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"vrfNames": VRF_NAME})

    print("\n-> Deploying VRF...")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, deploy_vrf.__name__)

    print("-> Success.")


def create_network(token):
    """ Create networks. """

    # Check if Network exists. If so, exit this function, else continue
    net = f"{ROOT_API}{VXLAN_FABRIC}/networks/{L2_NETWORK_NAME}"
    resp_net_existance = check_vrf_network_existance(net, token)

    if resp_net_existance == 200:
        print("-> Network exists. Moving onto next steps")

    if resp_net_existance != 200:
        url = f"{ROOT_API}{VXLAN_FABRIC}/networks"

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

        print("\n-> Creating Network...")
        resp = url_ok(url, headers, payload, request_method="POST")
        check_response_code(resp.status_code, create_network.__name__)

        print("-> Success.")


def attach_network(token):
    """ Attach network to switches and assing access ports. """

    url = f"{ROOT_API}{VXLAN_FABRIC}/networks/attachments"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    dev_serial_result = dbcontent.dev_serial(dbcontent.master_list)

    serial_swports_result = dbcontent.serial_switchports(dbcontent.master_list)

    vrf_lan_attach_list = []

    for serial in dev_serial_result.values():
        if serial in serial_swports_result.keys():
            lan_attachment_template = {
                "fabric": VXLAN_FABRIC,
                "networkName": L2_NETWORK_NAME,
                "serialNumber": serial,
                "switchPorts": serial_swports_result[serial],
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

    attachlist_vrf_lan_build = [{
        "networkName": L2_NETWORK_NAME,
        "lanAttachList": vrf_lan_attach_list
    }]

    payload = json.dumps(attachlist_vrf_lan_build)

    print("\n-> Attaching Network...")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, attach_network.__name__)

    resp_text_output = resp.json()
    check_validity(resp_text_output)

    print("-> Success.")


def deploy_network(token):
    """ Deploy the networks. """

    url = f"{ROOT_API}{VXLAN_FABRIC}/networks/deployments"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"networkNames": L2_NETWORK_NAME})

    print("\n-> Deploying network and interfaces...")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, deploy_network.__name__)

    print("-> Success.")


####################################
####################################

####################################
# *** Executing Program ***
####################################
def main():
    """ Main section to run functions. """

    tok = login()
    print("Please wait...")
    time.sleep(4)

# For troubleshooting, call this from within fuction 'create_vrf(tok)
#    check_vrf_existance(tok)

    create_vrf(tok)
    print("Please wait...")
    time.sleep(8)

    attach_vrf_new(tok)
    print("Please wait...")
    time.sleep(10)

    deploy_vrf(tok)
    print("Please wait...")
    time.sleep(15)

    create_network(tok)
    print("Please wait...")
    time.sleep(8)

    attach_network(tok)
    print("Please wait...")
    time.sleep(10)

    deploy_network(tok)
    print("Please wait...")
    time.sleep(15)


if __name__ == '__main__':
    main()
    print("\nProgram Completed!")
