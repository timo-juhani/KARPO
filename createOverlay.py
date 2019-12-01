import requests
import json
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# LOGIN CREDENTIALS

apic = "https://sandboxapicdc.cisco.com"
user = "admin"
pwd = "ciscopsdt"

# DEFINE FUNCTIONS

def login():
    url = apic + "/api/aaaLogin.json"
    payload = {"aaaUser":{"attributes":{"name": user,"pwd": pwd}}}
    header = {"content-type": "application/json"}
                    
    r = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    r_json = r.json()

    auth_token = r_json["imdata"][0]["aaaLogin"]["attributes"]["token"]
    cookie = {"APIC-Cookie": auth_token}
    return cookie

def createTenant(tenant, cookie):
    url = apic + "/api/node/mo/uni/tn-" + tenant + ".json"
    header = {"content-type": "application/json"}
    payload = {
                "fvTenant": {
                    "attributes": {
                        "name": tenant,
                        "status": "created"
                        }
                    }
                }

    r = requests.post(url, data=json.dumps(payload), cookies=cookie, headers=header, verify=False)

    if r.status_code == 200:
        print("[+] tenant tn-" + tenant + " was created.")
    elif r.status_code == 400:
        print("[-] tenant tn-" + tenant + " was not created.")

def createApp(tenant, app, cookie):
    url = apic + "/api/node/mo/uni/tn-" + tenant + "/ap-" + app + ".json"
    header = {"content-type": "application/json"}
    payload = {
                "fvAp": {
                    "attributes": {
                        "name": app,
                        "status": "created"
                        }
                    }
                }
    r = requests.post(url, data=json.dumps(payload), cookies=cookie, headers=header, verify=False)

    if r.status_code == 200:
        print("[+] aplication profile " + app + " was created.")
    elif r.status_code == 400:
        print("[-] aplication profile " + app + " was not created.")

def createVrf(tenant, vrf, cookie):
    url = apic + "/api/node/mo/uni/tn-" + tenant + "/ctx-" + vrf + ".json"
    header = {"content-type": "application/json"}
    payload = {
                "fvCtx": {
                    "attributes": {
                        "name": vrf,
                        "status": "created"
                        }
                    }
                }

    r = requests.post(url, data=json.dumps(payload), cookies=cookie, headers=header, verify=False)

    if r.status_code == 200:
        print("[+] VRF " + vrf + " was created.")
    elif r.status_code == 400:
        print("[-] VRF profile " + vrf + " was not created.")

def createBd(tenant, vrf, bd, cookie):
    url = apic + "/api/node/mo/uni/tn-" + tenant + "/BD-" + bd + ".json"
    header = {"content-type": "application/json"}
    payload = {
                "fvBD": {
                    "attributes": {
                        "name":bd,
                        "status":"created"
                        },
                    "children": [
                        {
                            "fvRsCtx": {
                                "attributes": {
                                    "tnFvCtxName": vrf,
                                    "status": "created,modified"
                                    }
                                }
                            }
                        ]
                    }
                }

    r = requests.post(url, data=json.dumps(payload), cookies=cookie, headers=header, verify=False)

    if r.status_code == 200:
        print("[+] Bridge domain " + bd + " was created.")
    elif r.status_code == 400:
        print("[-] Bridge domain " + bd + " was not created.")

def createEpg(tenant, app, epg, bd, cookie):
    url = apic + "/api/node/mo/uni/tn-" + tenant + "/ap-" + app + "/epg-" + epg + ".json"
    header = {"content-type": "application/json"}
    payload = {
                "fvAEPg": {
                    "attributes": {
                        "name":epg,
                        "status":"created"
                        },
                    "children": [
                        {
                            "fvRsBd": {
                                "attributes": {
                                    "tnFvBDName": bd,
                                    "status":"created,modified"
                                    }
                                }
                            }
                        ]
                    }
                }

    r = requests.post(url, data=json.dumps(payload), cookies=cookie, headers=header, verify=False)

    if r.status_code == 200:
        print("[+] EPG " + epg + " was created.")
    elif r.status_code == 400:
        print("[-] EPG " + epg + " was not created.")

def createFilter(tenant, filt, entry, ethertype, ip_protocol, port_lower, port_upper,  cookie):
    url = apic + "/api/node/mo/uni/tn-" + tenant + ".json"
    header = {"content-type": "application/json"}
    payload = {  
                "vzFilter":{  
                    "attributes": {  
                        "name": filt,
                        "status": "created"
                    },
                    "children":[  
                        {  
                            "vzEntry":{  
                                "attributes":{  
                                    "dFromPort": port_lower,
                                    "dToPort": port_upper,
                                    "etherT": ethertype,
                                    "name": entry,
                                    "prot": ip_protocol,
                                    "status":"created"
                                    }
                                }
                            }
                        ]   
                    }
                }

    r = requests.post(url, data=json.dumps(payload), cookies=cookie, headers=header, verify=False)

    if r.status_code == 200:
        print("[+] Filter " + filt + " was created.")
    elif r.status_code == 400:
        print("[-] Filter " + filt + " was not created.")     


# EXECUTE TASKS

cookie = login()

with open("configuration.json") as configuration:
    config_data = json.load(configuration)
    
    for tenant in config_data["tenants"]:
        print("[!] Create overlay: " + tenant.upper())
        createTenant(tenant, cookie)
        app = config_data["tenants"][tenant]["ap"]
        createApp(tenant, app, cookie)
        vrf = config_data["tenants"][tenant]["vrf"]
        createVrf(tenant, vrf, cookie)
        bd = config_data["tenants"][tenant]["bd"]
        createBd(tenant, vrf, bd, cookie)
        
        for e in range(len(config_data["tenants"][tenant]["epg"])):
            epg = config_data["tenants"][tenant]["epg"][e]
            createEpg(tenant, app, epg, bd, cookie)

        for f in config_data["filters"]:
            filt = config_data["filters"][f]["filt"]
            entry = config_data["filters"][f]["entry"]
            ethertype = config_data["filters"][f]["ethertype"]
            ip_protocol = config_data["filters"][f]["ip_protocol"]
            port_lower = config_data["filters"][f]["port_lower"]
            port_upper = config_data["filters"][f]["port_upper"]
            createFilter(tenant, filt, entry, ethertype, ip_protocol, port_lower, port_upper, cookie)
        
        print("[!] Moving to the next overlay")
        print("\n")
        
    print("[!] Overlay provisioning completed!")