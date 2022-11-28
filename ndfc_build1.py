import requests
import json
import time
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Enter credentials and server IP
cred_encode = 'ENTER BASE 64 CREDS'
dcnm_server = "10.91.86.229"
user = "admin"
password = "C1sc0_123"

#########################
# L3 VRF Variable
vrf_Vlan_Name = "VRF-522"
vrf_Segment_Id = "50222"
vrf_Name = "cpVRF-50222"
vrf_Vlan_Id = "2222"
bgp_asn = "65222"
vxlan_fabric = "Demo1"
vrf_vlan = "2222"

##########################
# L2 VNI Variables, a better naming convention and organization is needed
# Switch 1 - "serialNumber": "9AUJQKLY4W2"
switch1 = "FDO210518NL"

# Switch 2 - "serialNumber": "9IA7BNRKJW9"
switch2 = "FDO20352B5P"

gateway_IpAddress = "172.222.222.1/24"
l2_vlan_Id = "2322"
l2_segment_Id = "30222"
l2_network_Name = "cpNetwork_30222"
switch1_switchPorts = "Ethernet1/26"
switch2_switchPorts = "Ethernet1/26"


def status_check(resp):
    if resp.status_code != 200:
        print("Error...")
        sys.exit()


def login(creds):
    print("Logging into DCNM...")
    url = "https://{}/login".format(dcnm_server)

    payload = json.dumps({
        "userName": user,
        "userPasswd": password,
        "domain": "local"
    })
    headers = {'Content-Type': 'application/json'}

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)
    data = json.loads(response.text)['token']
    print(data)
    return data


def create_vrf(token):
    print("\nCreating VRF...")
    url = "https://{0}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{1}/vrfs".format(dcnm_server, vxlan_fabric)

    payload = \
    '''    {
        "fabric": "Demo1",
        "vrfName": "cpVRF2",
        "vrfTemplate": "Default_VRF_Universal",
        "vrfExtensionTemplate": "Default_VRF_Extension_Universal",
        "vrfTemplateConfig": "{\\"advertiseDefaultRouteFlag\\":\\"true\\",\\"routeTargetImport\\":\\"\\",\\"vrfVlanId\\":\\"2001\\",\\"isRPExternal\\":\\"false\\",\\"vrfDescription\\":\\"\\",\\"disableRtAuto\\":\\"false\\",\\"L3VniMcastGroup\\":\\"\\",\\"maxBgpPaths\\":\\"1\\",\\"maxIbgpPaths\\":\\"2\\",\\"vrfSegmentId\\":\\"55321\\",\\"routeTargetExport\\":\\"\\",\\"ipv6LinkLocalFlag\\":\\"true\\",\\"vrfRouteMap\\":\\"FABRIC-RMAP-REDIST-SUBNET\\",\\"routeTargetExportMvpn\\":\\"\\",\\"ENABLE_NETFLOW\\":\\"false\\",\\"configureStaticDefaultRouteFlag\\":\\"true\\",\\"tag\\":\\"12345\\",\\"rpAddress\\":\\"\\",\\"trmBGWMSiteEnabled\\":\\"false\\",\\"nveId\\":\\"1\\",\\"routeTargetExportEvpn\\":\\"\\",\\"NETFLOW_MONITOR\\":\\"\\",\\"bgpPasswordKeyType\\":\\"3\\",\\"bgpPassword\\":\\"\\",\\"mtu\\":\\"9216\\",\\"multicastGroup\\":\\"\\",\\"routeTargetImportMvpn\\":\\"\\",\\"isRPAbsent\\":\\"false\\",\\"advertiseHostRouteFlag\\":\\"false\\",\\"vrfVlanName\\":\\"\\",\\"trmEnabled\\":\\"false\\",\\"loopbackNumber\\":\\"\\",\\"asn\\":\\"65111\\",\\"vrfIntfDescription\\":\\"\\",\\"routeTargetImportEvpn\\":\\"\\",\\"vrfName\\":\\"cpVRF2\\"}",
        "tenantName": null,
        "vrfId": 55321,
        "serviceVrfTemplate": null,
        "source": null,
        "hierarchicalKey": "Demo1"
    }'''

    headers = {
        'Content-Type': 'application/json',
        'Authorization': str(token)
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)

    #print(response.text)


def attach_vrf(token):
    print("\nAttaching VRF...")
    url = "https://{0}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{1}/vrfs/attachments".format(dcnm_server, vxlan_fabric)
    
    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps([
        {
            "vrfName": "cpVRF2",
            "lanAttachList": [
        {
            "fabric": "Demo1",
            "vrfName": "cpVRF2",
            "serialNumber": "FDO210518NL",
            "vlan": 2004,
            "freeformConfig": "",
            "deployment": True,
            "extensionValues": "",
            "instanceValues": "{\"loopbackId\":\"\",\"loopbackIpAddress\":\"\",\"loopbackIpV6Address\":\"\"}"
        },
        {
            "fabric": "Demo1",
            "vrfName": "cpVRF2",
            "serialNumber": "FDO20352B5P",
            "vlan": 2004,
            "freeformConfig": "",
            "deployment": True,
            "extensionValues": "",
            "instanceValues": "{\"loopbackId\":\"\",\"loopbackIpAddress\":\"\",\"loopbackIpV6Address\":\"\"}"
        }
        ]
    }
    ])

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)

    #print(response.text)
    status_check(response)


def deploy_vrf(token):
    print("\nDeploying VRF...")
    url = "https://{0}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{1}/vrfs/deployments".format(dcnm_server, vxlan_fabric)

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"vrfNames": "cpVRF2"})

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)

    #print(response)
    status_check(response)


def create_network(token):
    print("\nCreating network...")
    #url = "https://{0}/rest/top-down/fabrics/{1}/networks".format(dcnm_server, vxlan_fabric)

    url = "https://{0}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{1}/networks".format(
        dcnm_server, vxlan_fabric)

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
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
                            "vrfName": "cpVRF2",
                            "isLayer2Only": "false",
                            "nveId": 1,
                            "vlanId": l2_vlan_Id,
                            "segmentId": l2_segment_Id,
                            "networkName": l2_network_Name
                            }

    payload = json.dumps({
        "fabric": vxlan_fabric,
        "vrf": "cpVRF2",
        "networkName": l2_network_Name,
        "displayName": l2_network_Name,
        "networkId": l2_segment_Id,
        "networkTemplateConfig": str(network_template_cfg),
        "networkTemplate": "Default_Network_Universal",
        "networkExtensionTemplate": "Default_Network_Extension_Universal",
        "source": None,
        "serviceNetworkTemplate": None,
        "interfaceGroups": None,
        "hierarchicalKey": None
    })

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)
    
    print(response.text)
    status_check(response)


def attach_network(token):
    print("\nAttaching network...")
    #url = "https://{0}/rest/top-down/fabrics/{1}/networks/attachments".format(dcnm_server, vxlan_fabric)
    url = "https://{0}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{1}/networks/attachments".format(
        dcnm_server, vxlan_fabric)

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps([
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
                    "untagged": False,
                    "freeformConfig": "",
                    "deployment": True,
                    "toPorts": "",
                    "extensionValues": "",
                    "instanceValues": ""
                },
                {
                    "fabric": vxlan_fabric,
                    "networkName": l2_network_Name,
                    "serialNumber": switch2,
                    "switchPorts": switch2_switchPorts,
                    "detachSwitchPorts": "",
                    "vlan": l2_vlan_Id,
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
        "POST", url, headers=headers, data=payload, verify=False)

    #print(response.text)
    status_check(response)


def deploy_network(token):
    print("\nDeploying network on interfaces...")
    #url = "https://{0}/rest/top-down/fabrics/{1}/networks/deployments".format(dcnm_server, vxlan_fabric)
    url = "https://{0}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{1}/networks/deployments".format(dcnm_server, vxlan_fabric)

    headers = {
        'Authorization': str(token),
        'Content-Type': 'application/json'
    }

    payload = json.dumps({"networkNames": l2_network_Name})

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)

    #print(response.text)
    #status_check(response)


def main():
    tok = login(cred_encode)
    time.sleep(4)

 #   print(logon)
 #   tok = logon.cookies
 #   print(tok)

 #   tok = get_token(logon)
 #   time.sleep(3)

#    create_vrf(tok)
#    time.sleep(8)

#    attach_vrf(tok)
#    time.sleep(10)

#    deploy_vrf(tok)
#    time.sleep(15)
    # Need longer wait time after deploy (10sec)

#    create_network(tok)
#    time.sleep(8)

#    attach_network(tok)
#    time.sleep(10)

#    deploy_network(tok)
#    time.sleep(15)
    # Need longer wait time after deploy (10sec)


if __name__ == '__main__':
    main()
    print("\nTadah!!!")
