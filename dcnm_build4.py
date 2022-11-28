import requests
import json
import time
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Enter credentials and server IP
cred_encode = 'YWRtaW46QzFzYzBfMTIz'
dcnm_server = "10.91.86.229"

#########################
# L3 VRF Variable
vrf_Vlan_Name = "VRF-522"
vrf_Segment_Id = "50222"
vrf_Name = "MyVRF_50222"
vrf_Vlan_Id = "2222"
bgp_asn = "65222"
vxlan_fabric = "SITE_10Av"
vrf_vlan = 2222

##########################
# L2 VNI Variables, a better naming convention and organization is needed
# Switch 1 - "serialNumber": "9AUJQKLY4W2"
switch1 = "FDO210518NL"

# Switch 2 - "serialNumber": "9IA7BNRKJW9"
switch2 = "FDO20352B5P"

gateway_IpAddress = "172.222.222.1/24"
l2_vlan_Id = "2322"
l2_segment_Id = "30222"
l2_network_Name = "MyNetwork_30222"
switch1_switchPorts = "Ethernet1/6"
switch2_switchPorts = "Ethernet1/6"


def status_check(resp):
    if resp.status_code != 200:
        print("Error...")
        sys.exit()


def login(creds):
    print("Logging into DCNM...")
    url = "https://{}/rest/logon".format(dcnm_server)

    payload = "{\"expirationTime\": 7200000}"
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Basic {}'.format(creds)
    }

    response = requests.request("POST", url, headers=headers, data = payload, verify=False).json()
    return response


def get_token(logon):
    print("\nExtracting Token....")
    token_key = logon['Dcnm-Token']
    return token_key


def create_vrf(token):
    print("\nCreating VRF...")
    url = "https://{0}/rest/top-down/fabrics/{1}/vrfs".format(dcnm_server, vxlan_fabric)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    vrf_template_cfg = {"vrfVlanName": vrf_Vlan_Name,
                        "vrfIntfDescription": "",
                        "vrfDescription": "",
                        "trmEnabled": "false",
                        "isRPExternal": "false",
                        "ipv6LinkLocalFlag": "true",
                        "trmBGWMSiteEnabled": "false",
                        "advertiseHostRouteFlag": "false",
                        "advertiseDefaultRouteFlag": "true",
                        "configureStaticDefaultRouteFlag": "true",
                        "mtu": "9216",
                        "tag": "12345",
                        "vrfRouteMap": "FABRIC-RMAP-REDIST-SUBNET",
                        "maxBgpPaths": "1",
                        "maxIbgpPaths": "2",
                        "rpAddress": "",
                        "loopbackNumber": "",
                        "L3VniMcastGroup": "",
                        "multicastGroup": "",
                        "vrfSegmentId": vrf_Segment_Id,
                        "vrfName": vrf_Name,
                        "vrfVlanId": vrf_Vlan_Id,
                        "nveId":1,
                        "asn": bgp_asn
                        }

    payload = {
        "fabric": vxlan_fabric,
        "vrfName": vrf_Name,
        "vrfId": vrf_Segment_Id,
        "vrfTemplate": "Default_VRF_Universal",
        "vrfTemplateConfig": str(vrf_template_cfg),
        "vrfExtensionTemplate": "Default_VRF_Extension_Universal",
        "source": None,
        "serviceVrfTemplate": None
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)
    status_check(response)


def attach_vrf(token):
    print("\nAttaching VRF...")
    url = "https://{0}/rest/top-down/fabrics/{1}/vrfs/attachments".format(dcnm_server, vxlan_fabric)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    payload = [
    {
        "vrfName": vrf_Name,
        "lanAttachList": [
            {
                "fabric": vxlan_fabric,
                "vrfName": vrf_Name,
                "serialNumber": switch1,
                "vlan": vrf_vlan,
                "freeformConfig": "",
                "deployment": "true",
                "extensionValues": "",
                "instanceValues": "{\"loopbackId\":\"\",\"loopbackIpAddress\":\"\",\"loopbackIpV6Address\":\"\"}"
            },
            {
                "fabric": vxlan_fabric,
                "vrfName": vrf_Name,
                "serialNumber": switch2,
                "vlan": vrf_vlan,
                "freeformConfig": "",
                "deployment": "true",
                "extensionValues": "",
                "instanceValues": "{\"loopbackId\":\"\",\"loopbackIpAddress\":\"\",\"loopbackIpV6Address\":\"\"}"
            }
        ]
    }
]

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)
    status_check(response)


def deploy_vrf(token):
    print("\nDeploying VRF...")
    url = "https://{0}/rest/top-down/fabrics/{1}/vrfs/deployments/".format(dcnm_server, vxlan_fabric)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    payload = {"vrfNames": vrf_Name}

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)
    status_check(response)


def create_network(token):
    print("\nCreating network...")
    url = "https://{0}/rest/top-down/fabrics/{1}/networks".format(dcnm_server, vxlan_fabric)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    network_template_cfg = {"gatewayIpAddress": gateway_IpAddress,
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
                            "vrfName": vrf_Name,
                            "isLayer2Only": "false",
                            "nveId":1,
                            "vlanId": l2_vlan_Id,
                            "segmentId": l2_segment_Id,
                            "networkName": l2_network_Name
                            }
      
    payload = {
        "fabric": vxlan_fabric,
        "vrf": "MyVRF_50000",
        "networkName": l2_network_Name,
        "displayName": l2_network_Name,
        "networkId": l2_segment_Id,
        "networkTemplateConfig": str(network_template_cfg),
        "networkTemplate": "Default_Network_Universal",
        "networkExtensionTemplate": "Default_Network_Extension_Universal",
        "source": None,
        "serviceNetworkTemplate": None
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)
    status_check(response)


def attach_network(token):
    print("\nAttaching network...")
    url = "https://{0}/rest/top-down/fabrics/{1}/networks/attachments".format(dcnm_server, vxlan_fabric)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    payload = [
        {
            "networkName": l2_network_Name,
            "lanAttachList": [
                {
                    "fabric": vxlan_fabric,
                    "networkName": l2_network_Name,
                    "serialNumber": switch1,
                    "switchPorts": switch1_switchPorts,
                    "detachSwitchPorts": "",
                    "vlan": l2_vlan_Id,
                    "dot1QVlan": 1,
                    "untagged": "false",
                    "freeformConfig": "",
                    "deployment": "true",
                    "extensionValues": "",
                    "instanceValues": ""
                },
                {
                    "fabric": vxlan_fabric,
                    "networkName": l2_network_Name,
                    "serialNumber": "9IA7BNRKJW9",
                    "switchPorts": switch2_switchPorts,
                    "detachSwitchPorts": "",
                    "vlan": l2_vlan_Id,
                    "dot1QVlan": 1,
                    "untagged": "false",
                    "freeformConfig": "",
                    "deployment": "true",
                    "extensionValues": "",
                    "instanceValues": ""
                }
            ]
        }
    ]

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)
    status_check(response)


def deploy_network(token):
    print("\nDeploying network on interfaces...")
    url = "https://{0}/rest/top-down/fabrics/{1}/networks/deployments".format(dcnm_server, vxlan_fabric)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    payload = {"networkNames": l2_network_Name}

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)
    status_check(response)


def main():
    logon = login(cred_encode)
    time.sleep(4)

 #   tok = get_token(logon)
 #   time.sleep(3)

 #   create_vrf(tok)
 #   time.sleep(8)

 #   attach_vrf(tok)
 #   time.sleep(10)

 #   deploy_vrf(tok)
 #   time.sleep(15)
    # Need longer wait time after deploy (10sec)

 #   create_network(tok)
 #   time.sleep(8)

 #   attach_network(tok)
 #   time.sleep(10)

 #   deploy_network(tok)
 #   time.sleep(15)
    # Need longer wait time after deploy (10sec)


if __name__ == '__main__':
    main()
    print("\nTadah!!!")
