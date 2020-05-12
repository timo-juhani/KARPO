import requests
import json
import urllib3
import jinja2

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
        print("[+] Object " + object + " was created.")
    elif status_code == 400:
        print("[-] Object " + object + " was not created.")

# ACI FUNCTIONS


def login(apic, header, configuration):
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
        print("[-] Login unsuccesful")
        return None


class AciObject:
    def __init__(self, name, type, url):
        self.name = name
        self.type = type
        self.url = url

    def create(self, header, cookie, template, configuration):
        r = post_payload(template, configuration, self.url, cookie, header)
        check_status_code(r.status_code, f'{self.type} {self.name}')
