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

    def createObject(self, header, cookie, template, configuration):
        r = post_payload(template, configuration, self.url, cookie, header)
        check_status_code(r.status_code, f'{self.type} {self.name}')

# EXECUTE TASKS


with open("configuration.json") as configuration:
    config_data = json.load(configuration)
    apic = config_data["apic"]
    header = {"content-type": "application/json"}
    cookie = login(apic, header, config_data)

    for t in config_data["tenants"]:
        tenant_url = apic + "/api/node/mo/uni/tn-" + t["name"] + ".json"
        tenant = AciObject(t["name"], "tenant", tenant_url)
        tenant.createObject(header, cookie, "tenant.j2", t)

        for a in t["ap"]:
            ap = AciObject(a["name"], "app_profile", tenant_url)
            ap.createObject(header, cookie, "app_profile.j2", a)

        for v in t["vrf"]:
            vrf = AciObject(v["name"], "vrf", tenant_url)
            vrf.createObject(header, cookie, "vrf.j2", v)

        for b in t["bd"]:
            bd = AciObject(b["name"], "bridge_domain", tenant_url)
            bd.createObject(header, cookie, "bridge_domain.j2", b)

        for f in t["filters"]:
            filt = AciObject(f["name"], "filter", tenant_url)
            filt.createObject(header, cookie, "filter.j2", f)

        for c in t["contracts"]:
            ctr = AciObject(f["name"], "contract", tenant_url)
            ctr.createObject(header, cookie, "contract.j2", c)
            for fe in c["filters"]:
                fentry_url = apic + "/api/node/mo/uni/tn-" + t["name"] + \
                    "/brc-" + c["name"] + "/subj-" + \
                    c["sub_name"] + ".json"
                fentry = AciObject(fe["name"], "filter_entry", fentry_url)
                fentry.createObject(header, cookie, "filter_entry.j2", fe)

        for e in t["epg"]:
            ap_url = apic + "/api/node/mo/uni/tn-" + \
                t["name"] + "/ap-" + e["ap"] + ".json"
            epg_url = apic + "/api/node/mo/uni/tn-" + \
                t["name"] + "/ap-" + e["ap"] + \
                "/epg-" + e["name"] + ".json"
            epg = AciObject(e["name"], "epg", ap_url)
            epg.createObject(header, cookie, "epg.j2", e)

            for p in e["prov_cont"]:
                pc = AciObject(p["name"], "provided_contract", epg_url)
                pc.createObject(header, cookie, "provided_contract.j2", p)

            for c in e["cons_cont"]:
                cc = AciObject(p["name"], "consumed_contract", epg_url)
                cc.createObject(header, cookie, "consumed_contract.j2", c)

            for s in e["static_bindings"]:
                sb = AciObject(s["encap"], "static_binding", epg_url)
                sb.createObject(header, cookie, "static_binding.j2", s)

        print("[!] Moving to the next overlay")
        print("\n")

    print("[!] Overlay provisioning completed!")
