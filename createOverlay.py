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


def createTenant(header, cookie, tenant):
    url = apic + "/api/node/mo/uni/tn-" + tenant["name"] + ".json"
    payload = render_payload("tenant.j2", tenant)
    r = requests.post(url, data=json.dumps(payload),
                      cookies=cookie, headers=header, verify=False)
    check_status_code(r.status_code, f'Tenant {tenant["name"]}')


def createApp(header, cookie, tenant, ap):
    url = apic + "/api/node/mo/uni/tn-" + tenant["name"] + ".json"
    payload = render_payload("app_profile.j2", ap)
    r = requests.post(url, data=json.dumps(payload),
                      cookies=cookie, headers=header, verify=False)
    check_status_code(r.status_code, f'AP {ap["name"]}')


def createVrf(header, cookie, tenant, vrf):
    url = apic + "/api/node/mo/uni/tn-" + tenant["name"] + ".json"
    payload = render_payload("vrf.j2", vrf)
    r = requests.post(url, data=json.dumps(payload),
                      cookies=cookie, headers=header, verify=False)
    check_status_code(r.status_code, f'VRF {vrf["name"]}')


def createBd(header, cookie, tenant, bd):
    url = apic + "/api/node/mo/uni/tn-" + tenant["name"] + ".json"
    payload = render_payload("bridge_domain.j2", bd)
    r = requests.post(url, data=json.dumps(payload),
                      cookies=cookie, headers=header, verify=False)
    check_status_code(r.status_code, f'BD {bd["name"]}')


def createEpg(header, cookie, tenant, epg):
    url = apic + "/api/node/mo/uni/tn-" + tenant["name"] + \
        "/ap-" + epg["ap"] + "/epg-" + epg["name"] + ".json"
    payload = render_payload("epg.j2", epg)
    r = requests.post(url, data=json.dumps(payload),
                      cookies=cookie, headers=header, verify=False)
    check_status_code(r.status_code, f'EPG {epg["name"]}')


def createFilter(header, cookie, tenant, filter):
    url = apic + "/api/node/mo/uni/tn-" + tenant["name"] + ".json"
    payload = render_payload("filter.j2", filter)
    r = requests.post(url, data=json.dumps(payload),
                      cookies=cookie, headers=header, verify=False)
    check_status_code(r.status_code, f'Filter {filter["name"]}')


def createContract(header, cookie, tenant, contract):
    url = apic + "/api/node/mo/uni/tn-" + tenant["name"] + ".json"
    payload = render_payload("contract.j2", contract)
    r = requests.post(url, data=json.dumps(payload),
                      cookies=cookie, headers=header, verify=False)
    check_status_code(r.status_code, f'Contract {contract["name"]}')


def addFilters(header, cookie, tenant, contract, filter_entry):
    url = apic + "/api/node/mo/uni/tn-" + tenant["name"] + \
        "/brc-" + contract["name"] + "/subj-" + contract["sub_name"] + ".json"
    payload = render_payload("filter_entry.j2", filter_entry)
    r = requests.post(url, data=json.dumps(payload),
                      cookies=cookie, headers=header, verify=False)
    check_status_code(r.status_code, f'Filter entry {filter_entry["name"]}')


# EXECUTE TASKS


with open("configuration.json") as configuration:
    config_data = json.load(configuration)
    apic = config_data["apic"]
    header = {"content-type": "application/json"}
    cookie = login(apic, header, config_data)

    for tenant in config_data["tenants"]:
        print("[!] Create overlay: " + tenant["name"].upper())
        createTenant(header, cookie, tenant)
        for a in tenant["ap"]:
            createApp(header, cookie, tenant, a)
        for v in tenant["vrf"]:
            createVrf(header, cookie, tenant, v)
        for b in tenant["bd"]:
            createBd(header, cookie, tenant, b)
        for e in tenant["epg"]:
            createEpg(header, cookie, tenant, e)
        for f in tenant["filters"]:
            createFilter(header, cookie, tenant, f)
        for c in tenant["contracts"]:
            createContract(header, cookie, tenant, c)
            for filter_entry in c["filters"]:
                addFilters(header, cookie, tenant, c, filter_entry)

        print("[!] Moving to the next overlay")
        print("\n")
    print("[!] Overlay provisioning completed!")
