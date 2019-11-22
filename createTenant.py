import requests
import json
import urllib3

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
        print("[+] tn-" + tenant + " was created.")
    elif r.status_code == 400:
        print("[-] tn-" + tenant + " was not created.")

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
               
# EXECUTE TASKS

cookie = login()
tenants = ["hirvi", "karhu", "janis", "koira"]

for tenant in tenants:
    createTenant(tenant, cookie)
    app = tenant + "-ap"
    createApp(tenant, app, cookie)
    
        


