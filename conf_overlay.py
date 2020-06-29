from aci import AciObject
from aci import login
from aci import glean_url
from aci import startup
import json


def main(tenant):

    with open("configuration_data.json") as configuration:
        apic, header, cookie, t = startup(configuration, tenant)
        tenant_url = glean_url(apic, tenant, "tenant", "")
        tnt = AciObject(tenant, "tenant", tenant_url)
        tnt.configure(header, cookie, "tenant.j2", t["tenant"][0])

        for a in t["aps"]:
            ap = AciObject(a["name"], "app_profile", tenant_url)
            ap.configure(header, cookie, "app_profile.j2", a)

        for v in t["vrfs"]:
            vrf = AciObject(v["name"], "vrf", tenant_url)
            vrf.configure(header, cookie, "vrf.j2", v)

        for b in t["bds"]:
            bd = AciObject(b["name"], "bridge_domain", tenant_url)
            bd.configure(header, cookie, "bridge_domain.j2", b)

        for f in t["filters"]:
            filt = AciObject(f["name"], "filter", tenant_url)
            filt.configure(header, cookie, "filter.j2", f)

        for c in t["contracts"]:
            ctr = AciObject(f["name"], "contract", tenant_url)
            ctr.configure(header, cookie, "contract.j2", c)

        for fe in t["filter_entries"]:
            fentry_url = glean_url(apic, tenant, "fentry", fe)
            fentry = AciObject(fe["name"], "filter_entry", fentry_url)
            fentry.configure(header, cookie, "filter_entry.j2", fe)

        for e in t["epgs"]:
            ap_url = glean_url(apic, tenant, "ap", e)
            epg = AciObject(e["name"], "epg", ap_url)
            epg.configure(header, cookie, "epg.j2", e)

        for p in t["prov_cont"]:
            epg_url = glean_url(apic, tenant, "epg", p)
            pc = AciObject(p["contract"], "provided_contract", epg_url)
            pc.configure(header, cookie, "provided_contract.j2", p)

        for c in t["cons_cont"]:
            epg_url = glean_url(apic, tenant, "epg", c)
            cc = AciObject(c["contract"], "consumed_contract", epg_url)
            cc.configure(header, cookie, "consumed_contract.j2", c)

        for d in t["phys_domains"]:
            epg_url = glean_url(apic, tenant, "epg", d)
            edom = AciObject(d["epg"], "epg_phys_domain for", epg_url)
            edom.configure(header, cookie, "epg_phys_domain.j2", d)

        for s in t["static_bindings"]:
            epg_url = glean_url(apic, tenant, "epg", s)
            sb = AciObject(s["encap"], "static_binding for", epg_url)
            sb.configure(header, cookie, "static_binding.j2", s)

        print(f"[!] Overlay {tenant} provisioning completed!")


if __name__ == "__main__":
    main("susi")
