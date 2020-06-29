import requests
import json
import urllib3
import jinja2
from getpass import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# HELP FUNCTIONS


def render_payload(template, configuration):
    payloadLoader = jinja2.FileSystemLoader(searchpath="payloads/")
    templateEnv = jinja2.Environment(loader=payloadLoader)
    t = template
    template = templateEnv.get_template(t)
    return json.loads(template.render(configuration))


def post_payload(template, configuration, url, cookie, header):
    payload = render_payload(template, configuration)
    return requests.post(url, data=json.dumps(payload),
                         cookies=cookie, headers=header, verify=False)


def check_status_code(status_code, object):
    if status_code == 200:
        print("[+] Object " + object + " was configured.")
    elif status_code == 400:
        print("[-] Object " + object + " was not configured.")


def confirm_connection(func):
    def wrap_func(*args, **kwargs):
        cookie = func(*args, **kwargs)
        if cookie is not False:
            return cookie
        else:
            exit()
    return wrap_func


# ACI DEFINITIONS

# Function to start the script with foundational information
def startup(configuration, tenant):
    conf = json.load(configuration)
    apic = conf["apic"]["info"][0]["host"]
    print(f"Configuration begins for {apic}")
    user = conf["apic"]["info"][0]["user"]
    #user = input("Username: ")
    pwd = conf["apic"]["info"][0]["password"]
    #pwd = getpass()
    credentials = {"user": user, "pwd": pwd}
    header = {"content-type": "application/json"}
    cookie = login(apic, header, credentials)
    t = conf[tenant]
    return apic, header, cookie, t

# Function to login to APIC
# It uses a decorator that checks whether network connection exists
@confirm_connection
def login(apic, header, configuration):
    try:
        url = apic + "/api/aaaLogin.json"
        payload = render_payload("login.j2", configuration)
        r = requests.post(url, data=json.dumps(payload),
                          headers=header, verify=False)

        if r.status_code == 200:
            print("[+] Login succesful.")
            r_json = r.json()
            auth_token = r_json["imdata"][0]["aaaLogin"]["attributes"]["token"]
            cookie = {"APIC-Cookie": auth_token}
            return cookie
        else:
            print("[-] Login unsuccesful due to wrong credentials")
            return False
    except:
        print("""
        APIC is unreachable! 
        - Check network connection
        - Check URL from: configuration_data.xlsx
        """)
        return False

# Function to put together URLs for REST methods so that URLS are not stored in the actual scripts


def glean_url(apic, tenant, object, conf):
    t_url = apic + "/api/node/mo/uni/tn-" + tenant
    if object == "tenant":
        return t_url + ".json"
    elif object == "ap":
        return t_url + "/ap-" + conf["ap"] + ".json"
    elif object == "epg":
        return t_url + "/ap-" + conf["ap"] + "/epg-" + conf["epg"] + ".json"
    elif object == "fentry":
        return t_url + "/brc-" + conf["contract"] + "/subj-" + conf["subject"] + ".json"
    elif object == "bd_subnet":
        return t_url + "/BD-" + conf["bd"] + "/subnet-[" + conf["ip"] + "].json"

# Class used to initialize each ACI MIT object with their information
# configure function simply posts the rendered REST call to APIC


class AciObject:
    def __init__(self, name, type, url):
        self.name = name
        self.type = type
        self.url = url

    def configure(self, header, cookie, template, configuration):
        r = post_payload(template, configuration, self.url, cookie, header)
        check_status_code(r.status_code, f'{self.type} {self.name}')

    # def state_check function to validate which objects are already there
