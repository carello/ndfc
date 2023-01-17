""" This program executes NDFC APIs to configure: VRFs, networks and deployment """

__version__ = "0.8"

# main_v8.py
#
# This version, uses data from ./data/dbcontent2.py which has a different dictionary structure.
#
# This version has more thorough error checking, (could be better),
# logging, and references the data in an external module called "data/dbcontent2".
# In this configuration it would allow you to reference external data sources like a .csv file.
# Formatting requirements are laid out in the dbcontent2.py file.
# Timers are very conservative, it could be tuned to shorten wait time...
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

from data import dbcontent2

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

# Coloring screen output. There could be compatability issues for different terminals.
BLACK   = "\033[0;30m"
RED     = "\033[0;31m"
REDBOLD = "\033[1;31m"
GREEN   = "\033[0;32m"
YELLOW  = "\033[0;33m"
WHITE   = "\033[0;37m"
NOCOLOR = "\033[0m"
BOLD    = "\033[1m"

# Enter Nexus Dashboard IP
ND_HOST = "https://10.91.86.229"

# Using environment variables for credentials, ARGPARSE could be implemented
USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']

# This is the most common api used in this script and am using this as a short cut.
ROOT_API = f"{ND_HOST}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/"

# L3 VRF Variables
ASN = "65111"
VRF_NAME = "cpVRF-50222"
VRF_SEGMENT_ID = "50222"
VRF_VLAN_ID = "2222"
VRF_VLAN_NAME = "VRF-522"
VXLAN_FABRIC = "Demo1"

# L2 VNI Variables
GATEWAY_IPADDRESS = "172.222.222.1/24"
L2_NETWORK_NAME = "cpNetwork_30222"
L2_SEGMENT_ID = "30222"
L2_VLAN_ID = "2322"

####################################
####################################


####################################
#       *** Functions ***
####################################


# progress bar animation
def animation_dot(sec):
    """Progress bar animation."""
    print(f"{YELLOW}Please wait while I run my tasks", end="")
    for _ in range(sec):
        time.sleep(1)
        print('.', end="", flush=True)
    print(f"{NOCOLOR}")


# Decorator prints out 'please wait for' so user knows something is still happening
def sleeper_timer_dec(secs):
    """ Sleeper Decorator """

    def waiting_print_dec(func):
        """ Simple decorator for print statement """

        @wraps(func)
        def wrapped(*args, **kwargs):
            # Place holder for before decoracted function

            inner_output = func(*args, **kwargs)
            # This will print after decorated function
            #print(f"{YELLOW}Please wait while I run my tasks", end="")
            # for _ in range(secs):
            #     time.sleep(1)
            #     print('.', end="", flush=True)
            animation_dot(secs)
            #print(f"{NOCOLOR}")
            return inner_output
        return wrapped
    return waiting_print_dec


# Logging decorator
def logging_dec():
    """ Logging decorator """

    def wrap_f(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            inner_output = func(*args, **kwargs)
            if LOGGING_STATUS:
                logging.debug("-> From function: %s", func.__name__)
            return inner_output
        return wrapped
    return wrap_f


@logging_dec()
def url_ok(uri, head, pay, request_method):
    """ Validate URL availability """

    try:
        #print("-> Checking URL request.")
        response = requests.request(request_method, uri, headers=head, data=pay, verify=False, timeout=30)
        response.raise_for_status()

    except requests.exceptions.RequestException as err:
        print(f"{REDBOLD}Request Exception found, please see logs. Exiting program.{NOCOLOR}")
        if LOGGING_STATUS:
            logging.debug(err)
        sys.exit(1)

        # This will raise an error on STDOUT and exit
        #raise SystemExit(err)

    return response


@logging_dec()
def check_response_code(resp_code, whereami):
    """
    Check response code
    """

    # Troubleshooting
    #print(f"whereami... source = {whereami}; checkpoint = {check_response_code.__name__}")

    if resp_code != 200:
        print(f"{REDBOLD}Something went wrong, invalid. Please check logs.{NOCOLOR}")
        if LOGGING_STATUS:
            logging.debug("Returned response code: %s from calling function: %s", resp_code, whereami)
        sys.exit(1)


def check_validity(resp_text, whereami):
    """ Check if api execution is proper, 'SUCCESS' """

    for item, output in resp_text.items():
        check_result = output
        if check_result.find("SUCCESS") == -1:
            print(f"{REDBOLD}Something went wrong, invalid.\nResponse: {resp_text} \nPlease check logs.{NOCOLOR}")
            if LOGGING_STATUS:
                out = item, output
                logging.debug("-> From calling function: %s, output: %s", whereami, out)
            sys.exit(1)


@logging_dec()
@sleeper_timer_dec(secs=4)
def login():
    """
    Login into ND and return a token. Status code returned should be 200
    >>> url = f"{ND_HOST}/login"
    >>> headers = {'Content-Type': 'application/json'}
    >>> payload = json.dumps({
    ...        "userName": USER,
    ...        "userPasswd": PASSWORD,
    ...        "domain": "local"
    ...        })
    >>> resp = url_ok(url, headers, payload, request_method="POST")
    >>> resp.status_code
    200
    """

    url = f"{ND_HOST}/login"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({
        "userName": USER,
        "userPasswd": PASSWORD,
        "domain": "local"
    })

    print("\n-> Logging into Nexus Dashboard.")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, login.__name__)

    print("-> Success.")
    data = json.loads(resp.text)['token']

    return data


@logging_dec()
def check_vrf_network_existance(vrf_net, token):
    """ Check if VRF or Network exists """

    headers = {
        'Content-Type': 'application/json',
        'Authorization': str(token)
    }

    payload = json.dumps({})
    print()

    # We only want to validate that the status_code is 200 and continue.
    # So using the following function won't work:
    #     resp = url_ok(vrf_net, headers, payload, request_method="GET")
    # So in this case, we'll need to call directly instead.
    # Rudimentary, could use more error checking.
    resp = requests.request("GET", vrf_net, headers=headers, data=payload, verify=False, timeout=30)

    return resp.status_code


@logging_dec()
@sleeper_timer_dec(secs=8)
def create_vrf(token):
    """
    Create a new VRF.
    """

    # Check if vrf exists. If so, exit this function, else continue
    vrf = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/{VRF_NAME}"

    headers = {
            'Content-Type': 'application/json',
            'Authorization': str(token)
        }

    resp_vrf_existance = check_vrf_network_existance(vrf, token)

    if resp_vrf_existance == 200:
        print("-> VRF exists. Moving onto next steps. ")

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

        print("\n-> Creating VRF.")
        resp = url_ok(url, headers, payload, request_method="POST")
        check_response_code(resp.status_code, create_vrf.__name__)

        print("-> Success.")


@logging_dec()
@sleeper_timer_dec(secs=10)
def attach_vrf_new(token):
    """ Creating iteration of switch dictionary """

    url = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/attachments"

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    # Get serial and switchport dictionary from data/dbcontent2.py
    serial_switchports_result = dbcontent2.serial_switchports(dbcontent2.master_list)

    #TEST/DEBUGGING
    #print(f"\n{serial_switchports_result}\n")
    #for serial in serial_switchports_result:
    #    print(serial)
    #print("\nExiting testing...")
    #sys.exit(1)

    lan_attach_list = []

    # This will reference the external master data from: ./data/dbcontent2
    # and extract the serial number.
    for serial in serial_switchports_result:
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

    print("\n-> Attaching VRF.")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, attach_vrf_new.__name__)

    print("-> Success.")


@logging_dec()
@sleeper_timer_dec(secs=15)
def deploy_vrf(token):
    """ Deploy VRF. """

    url = f"{ROOT_API}{VXLAN_FABRIC}/vrfs/deployments"
    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"vrfNames": VRF_NAME})

    print("\n-> Deploying VRF.")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, deploy_vrf.__name__)

    print("-> Success.")


@logging_dec()
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

        print("-> Creating Network.")
        resp = url_ok(url, headers, payload, request_method="POST")
        check_response_code(resp.status_code, create_network.__name__)

        print("-> Success.")


@logging_dec()
@sleeper_timer_dec(secs=15)
def attach_network(token):
    """ Attach network to switches and assing access ports. """

    url = f"{ROOT_API}{VXLAN_FABRIC}/networks/attachments"
    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    # Dictionary of serial number and switchports
    serial_swports_result = dbcontent2.serial_switchports(dbcontent2.master_list)

    #TEST/DEBUGGING
    # print(f"\n{serial_swports_result}\n")
    # for serial, switchports in serial_swports_result.items():
    #     print(serial, switchports)
    # print("\nExiting testing...")

    vrf_lan_attach_list = []

    # This will reference the external master data from: ./data/dbcontent2
    # for the serial number and switchports to be deployed. It cross references
    # two dictionaries: 'device_name/serial_num' and 'serial_num/switchports',
    # serial_num is the key. In its current implmentation, all that really is
    # needed is the serial_num/switcports dict - however, I started on this path
    # and didn't want to redo. The upside, is that if we ever need to reference
    # the device name, we should be good to do.
    for serial, switchports in serial_swports_result.items():
        lan_attachment_template = {
            "fabric": VXLAN_FABRIC,
            "networkName": L2_NETWORK_NAME,
            "serialNumber": serial,
            "switchPorts": switchports,
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

    print("\n-> Attaching Network.")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, attach_network.__name__)

    resp_text_output = resp.json()
    check_validity(resp_text_output, attach_network.__name__)

    print("-> Success.")


# Deploy the network after a recalculation
@logging_dec()
@sleeper_timer_dec(secs=15)
def deploy_network(token):
    """ Deploy the networks. """

    url = f"{ROOT_API}{VXLAN_FABRIC}/networks/deployments"
    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"networkNames": L2_NETWORK_NAME})

    print("\n-> Deploying network and interfaces.")
    resp = url_ok(url, headers, payload, request_method="POST")
    check_response_code(resp.status_code, deploy_network.__name__)

    print("-> Success.")


# Recalculate and save the config
@logging_dec()
#@sleeper_timer_dec(secs=10)
def deploy(token):
    """ Recalculate and save the config """

    url = f"{ND_HOST}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/control/fabrics/{VXLAN_FABRIC}/config-deploy"
    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({})

    print("\n-> Deploying config...")
    resp = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=30)
    check_response_code(resp.status_code, deploy.__name__)
    #time.sleep(10)
    animation_dot(10)
    #print("HERE D")

    # if resp.status_code == 200:
    #     print("-> Deployment complete.")
    # elif resp.status_code != 200:
    #     raise Exception("ERROR has occurred")
    #print("HERE DD")


# Recalculate and save the config
@logging_dec()
def recal_save(token):
    """ Recalculate and save the config """

    url = f"{ND_HOST}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/control/fabrics/{VXLAN_FABRIC}/config-save"
    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({})

    print("\n-> Recalculating and saving config...")
    resp = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=30)
    #check_response_code(resp.status_code, recal_save.__name__)
    #time.sleep(10)
    animation_dot(10)

    if resp.status_code != 200:
        print(f"Error from function: {recal_save.__name__}")
        raise Exception(f"{REDBOLD}ERROR has occurred, check logs.{NOCOLOR}")

    #deploy(token)
    #print("HERE B")


@logging_dec()
def get_deployment_state(token):
    """ Get deployment status """

    url = f"{ROOT_API}{VXLAN_FABRIC}/networks/{L2_NETWORK_NAME}/status"
    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({})

    print("\n-> Getting fabric status.")
    resp = url_ok(url, headers, payload, request_method="GET")

    json_data = json.loads(resp.text)
    status_result = json_data["networkStatus"]
    print(f"-> Network status: {status_result}")

    return status_result


# Check the state of the deployment eg. 'PENDING' or 'DEPLOYED" or 'NA etc...'
@logging_dec()
def checking_state(token):
    """ Check state of deployment """

    state = get_deployment_state(token)

    # Troubleshooting, comment out above line and uncomment the following line
    #state = "MOCK"

    # Determine the number of attempts to deploy
    count = 2
    while count > 0:
        if count == 1:
            print("\n-> Somthing isn't right.")
            print(f"{REDBOLD}-> Please check NDFC. Exiting.{NOCOLOR}")
            sys.exit(1)
        elif state not in ("PENDING", "DEPLOYED"):
            count -= 1
            print(f"\n-> Iteration countdown = {count}: {RED}Fabric not in steady state = {state}{NOCOLOR}")
            recal_save(token)
            deploy(token)
            state = get_deployment_state(token)
            # Troubleshooting, comment out above line and uncomment the following line
            #state = "MOCK ME"
        elif state == "PENDING":
            #print("HERE A")
            recal_save(token)
            deploy(token)
            #print("Here AA")
            count = 0
        elif state == "DEPLOYED":
            print("-> Success: Configuration has been deployed.")
            count = 0


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

    checking_state(tok)


if __name__ == '__main__':
    main()
    print(f"\n{BOLD}Program Completed!{NOCOLOR}")
