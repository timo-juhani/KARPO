import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def login(user, pwd):
    url = "https://sandboxapicdc.cisco.com/api/aaaLogin.json"
    payload = {"aaaUser":{"attributes":{"name": user,"pwd": pwd}}}
    header = {"content-type": "application/json"}
                    
    r = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    r_json = r.json()

    auth_token = r_json["imdata"][0]["aaaLogin"]["attributes"]["token"]
    cookie = {"APIC-Cookie": auth_token}
    return cookie

user = "admin"
pwd = "ciscopsdt"
cookie = login(user, pwd)
print(cookie)
