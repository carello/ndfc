import requests
import json
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


cred_encode = 'ENTER BASE64 CREDS'
dcnm_server = "10.91.86.220"


def login(creds):
    print("Logging into to DCNM...")
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
    url = "https://{}/rest/top-down/fabrics/SITE_10Av/vrfs".format(dcnm_server)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    vrf_template_cfg = {"vrfVlanName": "VRF-001",
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
                        "vrfSegmentId": "50000",
                        "vrfName": "MyVRF_50000",
                        "vrfVlanId": "2000",
                        "nveId":1,
                        "asn": "65111"
                        }

    payload = {
        "fabric": "SITE_10Av",
        "vrfName": "MyVRF_50000",
        "vrfId": "50000",
        "vrfTemplate": "Default_VRF_Universal",
        "vrfTemplateConfig": str(vrf_template_cfg),
        "vrfExtensionTemplate": "Default_VRF_Extension_Universal",
        "source": None,
        "serviceVrfTemplate": None
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)


def attach_vrf(token):
    print("\nAttaching VRF...")
    url = "https://{}/rest/top-down/fabrics/SITE_10Av/vrfs/attachments".format(dcnm_server)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    payload = [
    {
        "vrfName": "MyVRF_50000",
        "lanAttachList": [
            {
                "fabric": "SITE_10Av",
                "vrfName": "MyVRF_50000",
                "serialNumber": "9AUJQKLY4W2",
                "vlan": 2000,
                "freeformConfig": "",
                "deployment": "true",
                "extensionValues": "",
                "instanceValues": "{\"loopbackId\":\"\",\"loopbackIpAddress\":\"\",\"loopbackIpV6Address\":\"\"}"
            },
            {
                "fabric": "SITE_10Av",
                "vrfName": "MyVRF_50000",
                "serialNumber": "9IA7BNRKJW9",
                "vlan": 2000,
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


def deploy_vrf(token):
    print("\nDeploying VRF...")
    url = "https://{}/rest/top-down/fabrics/SITE_10Av/vrfs/deployments/".format(dcnm_server)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    payload = {"vrfNames": "MyVRF_50000"}

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)


def create_network(token):
    print("\nCreating network...")
    url = "https://{}/rest/top-down/fabrics/SITE_10Av/networks".format(dcnm_server)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    network_template_cfg = {"gatewayIpAddress": "172.27.1.1/24",
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
                            "vrfName": "MyVRF_50000",
                            "isLayer2Only": "false",
                            "nveId":1,
                            "vlanId": "2300",
                            "segmentId": "30000",
                            "networkName": "MyNetwork_30000"
                            }
      
    payload = {
        "fabric": "SITE_10Av",
        "vrf": "MyVRF_50000",
        "networkName": "MyNetwork_30000",
        "displayName": "MyNetwork_30000",
        "networkId": "30000",
        "networkTemplateConfig": str(network_template_cfg),
        "networkTemplate": "Default_Network_Universal",
        "networkExtensionTemplate": "Default_Network_Extension_Universal",
        "source": None,
        "serviceNetworkTemplate": None
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)


def attach_network(token):
    print("\nAttaching network...")
    url = "https://{}/rest/top-down/fabrics/SITE_10Av/networks/attachments".format(dcnm_server)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    payload = [
        {
            "networkName": "MyNetwork_30000",
            "lanAttachList": [
                {
                    "fabric": "SITE_10Av",
                    "networkName": "MyNetwork_30000",
                    "serialNumber": "9AUJQKLY4W2",
                    "switchPorts": "Ethernet1/6",
                    "detachSwitchPorts": "",
                    "vlan": "2300",
                    "dot1QVlan": 1,
                    "untagged": "false",
                    "freeformConfig": "",
                    "deployment": "true",
                    "extensionValues": "",
                    "instanceValues": ""
                },
                {
                    "fabric": "SITE_10Av",
                    "networkName": "MyNetwork_30000",
                    "serialNumber": "9IA7BNRKJW9",
                    "switchPorts": "Ethernet1/7",
                    "detachSwitchPorts": "",
                    "vlan": "2300",
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


def deploy_network(token):
    print("\nDeploying network on interfaces...")
    url = "https://{}/rest/top-down/fabrics/SITE_10Av/networks/deployments".format(dcnm_server)
    headers = {
        'Dcnm-Token': token,
        'Content-Type': 'application/json',
    }

    payload = {"networkNames": "MyNetwork_30000"}

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response)


def main():
    logon = login(cred_encode)
    time.sleep(5)

    tok = get_token(logon)
    time.sleep(5)

    create_vrf(tok)
    time.sleep(10)

    attach_vrf(tok)
    time.sleep(10)

    deploy_vrf(tok)
    time.sleep(15)
    # Need longer wait time after deploy (10sec)

    create_network(tok)
    time.sleep(10)

    attach_network(tok)
    time.sleep(10)

    deploy_network(tok)
    time.sleep(15)
    # Need longer wait time after deploy (10sec)


if __name__ == '__main__':
    main()
    print("\nTadah!!!")

