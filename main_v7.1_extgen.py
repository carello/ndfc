""" This program executes NDFC APIs to configure: VRFs, networks and deployment """

# This version has more thorough error checking, (could be better),
# logging, and references the data in an external module called "data/dbcontent".
# In this configuration it would allow you to reference external data sources like a .csv file.
# Formatting requirements are laid out in the dbcontent.py file.
#
# To view DocStrings run: 'python -m pydoc ./ndfc_build3.py' or 'python -m pydoc -b'


import json
import time
import sys
import os
import logging
from functools import wraps
import requests
import urllib3

from data import dbcontent

urllib3.disable_warnings(category = urllib3.exceptions.InsecureRequestWarning)

# Set up switches. Perhaps implement ARGPARSE in future
LOGGING_STATUS = True

logging.basicConfig(filename='ndfc.log', format="%(asctime)s - %(message)s",
    encoding='utf-8', level=logging.DEBUG)

# Place a blank line in log file at start of execution
logging.info("\n")


####################################################
#          *** Set up CONSTANTS ***
# This also could be implemented using a csv file
####################################################

# Coloring screen output
BLACK   = "\033[0;30m"
RED     = "\033[0;31m"
REDBOLD = "\033[1;31m"
GREEN   = "\033[0;32m"
YELLOW  = "\033[0;33m"
WHITE   = "\033[0;37m"
NOCOLOR = "\033[0m"
BOLD    = "\033[1m"

# Enter credentials and server IP
ND_HOST = "https://10.91.86.229"

# Using environment variables, ARGPARSE could be implemented
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
#       *** Functions ***
####################################

# Decorator prints out 'please wait for' so user knows something is still happening
def sleeper_timer_dec(secs):
    """ Sleeper timer """

    def waiting_print_dec(func):
        """ Simple decorator for print statement """

        @wraps(func)
        def wrapped(*args, **kwargs):
            # Place holder for before decoracted function

            # Start of inner capabilities
            inner_output = func(*args, **kwargs)
            # This will print after decorated function
            print(f"{YELLOW}Please wait while I run my tasks...{NOCOLOR}")
            time.sleep(secs)
            return inner_output
        return wrapped
    return waiting_print_dec


# Test Decorator
def say_hello_dec(hi_ho):
    """ Say hello """
    @wraps(hi_ho)
    def wrapped(*args, **kwargs):
        # Place holder for before decoracted function
        print("TEST Dec: Say HELLO...")
        # Start of inner capabilities
        inner_output = hi_ho(*args, **kwargs)
        # This will print after decorated function
        return inner_output
    return wrapped


# Experimenting using an external url generator to abstract from functions.
# I don't think this is adding value
def url_generator(dst_url, token):
    """ Generate URL and headers """

    url_header_dict = []
    dst_url_result = f"{ROOT_API}{VXLAN_FABRIC}/{dst_url}"

    headers = {
            'Content-Type': 'application/json',
            'Authorization': str(token)
        }

    url_header_dict = [dst_url_result, headers]

    return url_header_dict


def url_ok(uri, head, pay, request_method):
    """ Validate URL availability """

    try:
        print("-> Checking URL request...")
        response = requests.request(request_method, uri, headers=head, data=pay, verify=False, timeout=4)
        response.raise_for_status()

    except requests.exceptions.RequestException as err:
        print(f"{REDBOLD}Request Exception found, please see logs. Exiting program...{NOCOLOR}")
        if LOGGING_STATUS:
            logging.debug(err)
        sys.exit(1)

        # This will raise an error on STDOUT and exit
        #raise SystemExit(err)

    return response


def check_response_code(resp_code, whereami):
    """ Check response code """

    # Troubleshooting
    #print(f"YY in 'check_responde_code'- {resp_code}")

    if resp_code != 200:
        print(f"{REDBOLD}Something went wrong, invalid. Please check logs.{NOCOLOR}")
        if LOGGING_STATUS:
            logging.debug("Returned response code: %s from calling function: %s", resp_code, whereami)
        sys.exit(1)


def check_validity(resp_text):
    """ Check if api execution is proper, 'SUCCESS' """

    for item, output in resp_text.items():
        check_result = output
        if check_result.find("SUCCESS") == -1:
            print(f"{REDBOLD}Something went wrong, invalid. Please check logs.{NOCOLOR}")
            if LOGGING_STATUS:
                out = item, output
                logging.debug(out)
            sys.exit(1)


@sleeper_timer_dec(secs=4)
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

    vrf_uri = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/{vrf_net}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': str(token)
    }

    payload = {}

    # We only want to validate that the status_code is 200 and continue.
    # So using the following function won't work:
    #     resp = url_ok(vrf_net, headers, payload, request_method="GET")
    # So in this case, we'll need to call directly instead.
    # Rudimentary, could use more error checking.
    resp = requests.request("GET", vrf_uri, headers=headers, data=payload, verify=False, timeout=4)

    print()
    return resp.status_code


# I'm trying the external url generator on this function.
@sleeper_timer_dec(secs=8)
def create_vrf(token):
    """ Create a new VRF. """

    # Check if vrf exists. If so, exit this function, else continue
    #vrf = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/{VRF_NAME}"
    resp_vrf_existance = check_vrf_network_existance(VRF_NAME, token)

    if resp_vrf_existance == 200:
        print("-> VRF exists. Moving onto next step. ")

    # Experimenting using an external URL generator...
    if resp_vrf_existance != 200:
        #url = f"{ROOT_API}{VXLAN_FABRIC}/vrfs"
        uri_header_result = url_generator("vrfs", token)

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

        url = uri_header_result[0]
        headers = uri_header_result[1]

        print("\n-> Creating VRF...")
        resp = url_ok(url, headers, payload, request_method="POST")
        check_response_code(resp.status_code, create_vrf.__name__)

        print("-> Success.")


@sleeper_timer_dec(secs=10)
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

    # This will reference the external master data from: ./data/dbcontent
    # for the device and serial number, and extract the serial number.
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


@sleeper_timer_dec(secs=15)
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


@sleeper_timer_dec(secs=8)
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


@sleeper_timer_dec(secs=10)
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

    # This will reference the external master data from: ./data/dbcontent
    # for the serial number and switchports to be deployed. It cross references
    # two dictionaries: 'device_name/serial_num' and 'serial_num/switchports',
    # serial_num is the key. In its current implmentation, all that really is
    # needed is the serial_num/switcports dict - however, I started on this path
    # and didn't want to redo. The upside, is that if we ever need to reference
    # the device name, we should be good to do.
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


@sleeper_timer_dec(secs=15)
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

    create_vrf(tok)

    attach_vrf_new(tok)

    deploy_vrf(tok)

    create_network(tok)

    attach_network(tok)

    deploy_network(tok)


if __name__ == '__main__':
    main()
    print(f"\n{BOLD}Program Completed!{NOCOLOR}")
