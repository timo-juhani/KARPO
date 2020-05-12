from aci import AciObject
from aci import login
import json


def main():

    with open("configuration.json") as configuration:
        config = json.load(configuration)
        apic = config["apic"]
        header = {"content-type": "application/json"}
        cookie = login(apic, header, config)

        for t in config["tenants"]:
            tenant_url = apic + "/api/node/mo/uni/tn-" + t["name"] + ".json"
            tenant = AciObject(t["name"], "tenant", tenant_url)
            tenant.create(header, cookie, "tenant.j2", t)

            for a in t["ap"]:
                ap = AciObject(a["name"], "app_profile", tenant_url)
                ap.create(header, cookie, config["tmpl"]["ap"], a)

            for v in t["vrf"]:
                vrf = AciObject(v["name"], "vrf", tenant_url)
                vrf.create(header, cookie, config["tmpl"]["vf"], v)

            for b in t["bd"]:
                bd = AciObject(b["name"], "bridge_domain", tenant_url)
                bd.create(header, cookie, config["tmpl"]["bd"], b)

            for f in t["filters"]:
                filt = AciObject(f["name"], "filter", tenant_url)
                filt.create(header, cookie, config["tmpl"]["fr"], f)

            for c in t["contracts"]:
                ctr = AciObject(f["name"], "contract", tenant_url)
                ctr.create(header, cookie, "contract.j2", c)
                for fe in c["filters"]:
                    fentry_url = apic + "/api/node/mo/uni/tn-" + t["name"] + \
                        "/brc-" + c["name"] + "/subj-" + \
                        c["sub_name"] + ".json"
                    fentry = AciObject(fe["name"], "filter_entry", fentry_url)
                    fentry.create(header, cookie, config["tmpl"]["fe"], fe)

            for e in t["epg"]:
                ap_url = apic + "/api/node/mo/uni/tn-" + \
                    t["name"] + "/ap-" + e["ap"] + ".json"
                epg_url = apic + "/api/node/mo/uni/tn-" + \
                    t["name"] + "/ap-" + e["ap"] + \
                    "/epg-" + e["name"] + ".json"
                epg = AciObject(e["name"], "epg", ap_url)
                epg.create(header, cookie, config["tmpl"]["eg"], e)

                for p in e["prov_cont"]:
                    pc = AciObject(p["name"], "provided_contract", epg_url)
                    pc.create(header, cookie, config["tmpl"]["pc"], p)

                for c in e["cons_cont"]:
                    cc = AciObject(p["name"], "consumed_contract", epg_url)
                    cc.create(header, cookie, config["tmpl"]["cc"], c)

                for s in e["static_bindings"]:
                    sb = AciObject(s["encap"], "static_binding", epg_url)
                    sb.create(header, cookie, config["tmpl"]["sb"], s)

            print("[!] Moving to the next overlay")
            print("\n")

        print("[!] Overlay provisioning completed!")


if __name__ == "__main__":
    main()
