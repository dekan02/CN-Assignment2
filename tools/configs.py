import ipaddress
import topology as T
from model import SUBNETS, subnet, loopback

ENABLE = "Lab@2026"
DNS = T.SERVERS["AD-DNS"]
CORE_VLANS = ["WIFI-STAFF", "WIFI-GUEST", "CORE-MGMT"]


def ipn(value):
    return ipaddress.ip_address(value)


def header(host):
    return [
        f"hostname {host}",
        "no ip domain-lookup",
        "service password-encryption",
        f"enable secret {ENABLE}",
        f"username admin privilege 15 secret {ENABLE}",
        "banner motd #Authorized access only#",
        "line con 0",
        " logging synchronous",
        "line vty 0 4",
        " login local",
        "exit",
    ]


def loop_lines(host):
    return ["interface Loopback0", f" ip address {loopback(host)} 255.255.255.255", " no shutdown", "exit"]


def routed(port, address, network, desc):
    return [
        f"interface {port}",
        f" description {desc}",
        " no switchport",
        f" ip address {address} {network.netmask}",
        " no shutdown",
        "exit",
    ]


def router_port(port, address, network, desc):
    return [
        f"interface {port}",
        f" description {desc}",
        f" ip address {address} {network.netmask}",
        " no shutdown",
        "exit",
    ]


def is_dhcp(s):
    return not (s.name.endswith("MGMT") or s.name.endswith("DMZ") or "SERVER" in s.name)


def dhcp_pool(s, part=None, parts=1):
    first = int(s.network.network_address) + 11
    last = int(s.network.broadcast_address) - 1
    lines = []
    if parts == 1:
        lines.append(f"ip dhcp excluded-address {s.network.network_address + 1} {ipaddress.ip_address(first - 1)}")
    else:
        mid = first + (last - first) // 2
        if part == 0:
            lines.append(f"ip dhcp excluded-address {s.network.network_address + 1} {ipaddress.ip_address(first - 1)}")
            lines.append(f"ip dhcp excluded-address {ipaddress.ip_address(mid + 1)} {ipaddress.ip_address(last)}")
        else:
            lines.append(f"ip dhcp excluded-address {s.network.network_address + 1} {ipaddress.ip_address(mid)}")
    lines += [
        f"ip dhcp pool P-{s.name}",
        f" network {s.network.network_address} {s.network.netmask}",
        f" default-router {s.gateway}",
        f" dns-server {DNS}",
        "exit",
    ]
    return lines


def vlan_db(subnets):
    lines = []
    for s in subnets:
        lines += [f"vlan {s.vlan}", f" name {s.name}", "exit"]
    return lines


def acl_for(kind, site):
    base = [
        " permit udp any eq bootpc any eq bootps",
        " permit udp any host 224.0.0.2 eq 1985",
    ]
    if kind == "guest":
        return base + [
            f" permit udp any host {DNS} eq domain",
            " deny ip any 10.0.0.0 0.255.255.255",
            " deny ip any 172.16.0.0 0.15.255.255",
            " deny ip any 192.168.0.0 0.0.255.255",
            " permit ip any any",
        ]
    local_server = T.SERVERS["NVR"] if site == "HCM" else str(subnet(f"{site}-SERVER").host(2))
    if kind == "cctv":
        return base + [f" permit ip any host {local_server}", " deny ip any any"]
    targets = [T.SERVERS["HIS-APP"], T.SERVERS["PACS"], T.SERVERS["LIS"]]
    if site != "HCM":
        targets.append(local_server)
    return base + [f" permit ip any host {t}" for t in targets] + [" deny ip any any"]


def acl_kind(s):
    if s.name.endswith("WIFI-GUEST"):
        return "guest"
    if s.name.endswith("CCTV"):
        return "cctv"
    if s.name.endswith("MEDDEV"):
        return "meddev"
    return None


def acl_block(kinds, site):
    lines = []
    for kind in sorted(set(kinds)):
        lines.append(f"ip access-list extended ACL-{kind.upper()}")
        lines += acl_for(kind, site)
        lines.append("exit")
    return lines


def svi_hsrp(s, group, priority, local):
    lines = [
        f"interface Vlan{s.vlan}",
        f" description {s.name}",
        f" ip address {local} {s.network.netmask}",
        f" standby {group} ip {s.gateway}",
        f" standby {group} priority {priority}",
        f" standby {group} preempt",
    ]
    kind = acl_kind(s)
    if kind:
        lines.append(f" ip access-group ACL-{kind.upper()} in")
    lines += [" no shutdown", "exit"]
    return lines


def ospf_lines(host, networks, passive_except):
    lines = ["router ospf 1", f" router-id {loopback(host)}", " passive-interface default"]
    for p in passive_except:
        lines.append(f" no passive-interface {p}")
    lines.append(f" network {loopback(host)} 0.0.0.0 area 0")
    for n in networks:
        lines.append(f" network {n.network_address} {n.hostmask} area 0")
    lines.append("exit")
    return lines


def hsrp_groups(subnets):
    return {s.vlan: i + 1 for i, s in enumerate(sorted(subnets, key=lambda x: x.vlan))}


def ds_config(host):
    building = host.split("-")[1][0]
    index = int(host[-1]) - 1
    group = "A" if building == "A" else "B"
    subs = [s for s in SUBNETS if s.site == "HCM" and s.group == group]
    groups = hsrp_groups(subs)
    lines = header(host) + ["ip routing", "spanning-tree mode rapid-pvst"] + vlan_db(subs) + loop_lines(host)
    for s in sorted(subs, key=lambda x: x.vlan):
        pos = groups[s.vlan] - 1
        primary = (pos % 2 == index)
        lines.append(f"spanning-tree vlan {s.vlan} priority {4096 if primary else 8192}")
    uplinks = []
    for core_idx, core in enumerate(("CORE1", "CORE2")):
        key = f"{host}-{core}"
        lines += routed(f"GigabitEthernet1/0/{core_idx + 1}", T.addr(key, 0), T.net(key), f"to {core}")
        uplinks.append(T.net(key))
    vlist = ",".join(str(s.vlan) for s in sorted(subs, key=lambda x: x.vlan))
    lines += [
        "interface GigabitEthernet1/0/3",
        f" description to ACC-{group}",
        " switchport mode trunk",
        f" switchport trunk allowed vlan {vlist}",
        " no shutdown",
        "exit",
        "interface GigabitEthernet1/0/4",
        f" description to {host[:-1]}{2 - index}",
        " switchport mode trunk",
        f" switchport trunk allowed vlan {vlist}",
        " no shutdown",
        "exit",
    ]
    kinds = [acl_kind(s) for s in subs if acl_kind(s)]
    lines += acl_block(kinds, "HCM")
    for s in sorted(subs, key=lambda x: x.vlan):
        pos = groups[s.vlan] - 1
        primary = (pos % 2 == index)
        local = s.gateway_a if index == 0 else s.gateway_b
        lines += svi_hsrp(s, groups[s.vlan], 110 if primary else 100, local)
    for s in sorted(subs, key=lambda x: x.vlan):
        if is_dhcp(s):
            lines += dhcp_pool(s, index, 2)
    svi_nets = [s.network for s in subs]
    lines += ospf_lines(host, uplinks + svi_nets, [f"GigabitEthernet1/0/{i}" for i in (1, 2)])
    return lines


def core_config(host):
    index = int(host[-1]) - 1
    other = "CORE2" if index == 0 else "CORE1"
    subs = [subnet(n) for n in CORE_VLANS]
    groups = hsrp_groups(subs)
    lines = header(host) + ["ip routing", "spanning-tree mode rapid-pvst"] + vlan_db(subs)
    lines += ["vlan 998", " name CORE-TRANSIT", "exit"] + loop_lines(host)
    for s in subs:
        lines.append(f"spanning-tree vlan {s.vlan},998 priority {4096 if index == 0 else 8192}")
    ospf_nets = []
    passive_except = []
    if index == 0:
        lines += routed("GigabitEthernet1/0/1", T.addr("fw-c1", 1), T.net("fw-c1"), "to FW-HCM inside")
    lines += [
        "interface GigabitEthernet1/0/2",
        f" description to {other}",
        " switchport mode trunk",
        " switchport trunk allowed vlan 320,330,399,998",
        " no shutdown",
        "exit",
        "interface Vlan998",
        " description core transit",
        f" ip address {T.addr('core-core', index)} {T.net('core-core').netmask}",
        " no shutdown",
        "exit",
    ]
    ospf_nets.append(T.net("core-core"))
    passive_except.append("Vlan998")
    port = 3
    for ds in ("DS-A1", "DS-A2", "DS-B1", "DS-B2"):
        key = f"{ds}-{host}"
        name = f"GigabitEthernet1/0/{port}"
        lines += routed(name, T.addr(key, 1), T.net(key), f"to {ds}")
        ospf_nets.append(T.net(key))
        passive_except.append(name)
        port += 1
    wan = "R-WAN1" if index == 0 else "R-WAN2"
    wkey = "c1-wan1" if index == 0 else "c2-wan2"
    lines += routed("GigabitEthernet1/0/7", T.addr(wkey, 0), T.net(wkey), f"to {wan}")
    ospf_nets.append(T.net(wkey))
    passive_except.append("GigabitEthernet1/0/7")
    lines += [
        "interface GigabitEthernet1/0/8",
        " description to WLC",
        " switchport mode trunk",
        " switchport trunk native vlan 399",
        " switchport trunk allowed vlan 320,330,399",
        " no shutdown",
        "exit",
    ]
    lines += acl_block(["guest"], "HCM")
    for s in subs:
        local = s.gateway_a if index == 0 else s.gateway_b
        priority = 110 if index == 0 else 100
        lines += svi_hsrp(s, groups[s.vlan], priority, local)
    for s in subs:
        if is_dhcp(s):
            lines += dhcp_pool(s, index, 2)
    ospf_nets += [s.network for s in subs]
    if index == 0:
        lines += [
            f"ip route 0.0.0.0 0.0.0.0 {T.addr('fw-c1', 0)}",
            f"ip route 10.10.36.64 255.255.255.240 {T.addr('fw-c1', 0)}",
            f"ip route 10.10.36.80 255.255.255.240 {T.addr('fw-c1', 0)}",
        ]
    lines += ospf_lines(host, ospf_nets, passive_except)
    if index == 0:
        lines.insert(-1, " default-information originate")
        lines.insert(-1, " redistribute static subnets")
    return lines


def access_ports(group):
    if group == "A":
        vlans = [110, 111, 112, 113, 114, 115, 170, 180, 160, 150, 112]
    else:
        vlans = [210, 211, 212, 213, 214, 215, 270, 280, 260, 250, 211]
    return [(f"FastEthernet0/{i + 1}", v) for i, v in enumerate(vlans)]


def acc_config(host):
    group = host[-1]
    subs = [s for s in SUBNETS if s.site == "HCM" and s.group == group]
    mgmt = subnet(f"{group}-MGMT")
    lines = header(host) + ["spanning-tree mode rapid-pvst"] + vlan_db(subs)
    vlist = ",".join(str(s.vlan) for s in sorted(subs, key=lambda x: x.vlan))
    for idx, ds in enumerate((f"DS-{group}1", f"DS-{group}2")):
        lines += [
            f"interface GigabitEthernet0/{idx + 1}",
            f" description to {ds}",
            " switchport mode trunk",
            f" switchport trunk allowed vlan {vlist}",
            " no shutdown",
            "exit",
        ]
    by_vlan = {s.vlan: s for s in subs}
    for port, vlan in access_ports(group):
        lines += [
            f"interface {port}",
            f" description {by_vlan[vlan].name}",
            " switchport mode access",
            f" switchport access vlan {vlan}",
            " spanning-tree portfast",
            " no shutdown",
            "exit",
        ]
    lines += [
        f"interface Vlan{mgmt.vlan}",
        f" ip address {mgmt.host(4)} {mgmt.network.netmask}",
        " no shutdown",
        "exit",
        f"ip default-gateway {mgmt.gateway}",
    ]
    return lines


def aux_ports(site):
    sw1 = [("FastEthernet0/1", 110), ("FastEthernet0/2", 111), ("FastEthernet0/3", 170), ("FastEthernet0/4", 180), ("FastEthernet0/5", 150), ("FastEthernet0/6", 110)]
    sw2 = [("FastEthernet0/1", 112), ("FastEthernet0/2", 113), ("FastEthernet0/3", 160), ("FastEthernet0/4", 300), ("FastEthernet0/5", 170)]
    return sw1, sw2


def aux_switch_config(site, number):
    host = f"SW-{site}-{number}"
    subs = [s for s in SUBNETS if s.site == site]
    mgmt = subnet(f"{site}-MGMT")
    ports = aux_ports(site)[number - 1]
    lines = header(host) + ["spanning-tree mode rapid-pvst"] + vlan_db(subs)
    vlist = ",".join(str(s.vlan) for s in sorted(subs, key=lambda x: x.vlan))
    lines += [
        "interface GigabitEthernet0/1",
        f" description {'to R-' + site if number == 1 else 'to SW-' + site + '-1'}",
        " switchport mode trunk",
        f" switchport trunk allowed vlan {vlist}",
        " no shutdown",
        "exit",
    ]
    if number == 1:
        lines += [
            "interface GigabitEthernet0/2",
            f" description to SW-{site}-2",
            " switchport mode trunk",
            f" switchport trunk allowed vlan {vlist}",
            " no shutdown",
            "exit",
        ]
    by_vlan = {s.vlan: s for s in subs}
    for port, vlan in ports:
        lines += [
            f"interface {port}",
            f" description {by_vlan[vlan].name}",
            " switchport mode access",
            f" switchport access vlan {vlan}",
            " spanning-tree portfast",
            " no shutdown",
            "exit",
        ]
    lines += [
        f"interface Vlan{mgmt.vlan}",
        f" ip address {mgmt.host(1 + number)} {mgmt.network.netmask}",
        " no shutdown",
        "exit",
        f"ip default-gateway {mgmt.gateway}",
    ]
    return lines


def crypto_lines(peer, acl_num, local_nets, remote_nets, key, iface):
    lines = [
        "crypto isakmp policy 10",
        " encryption aes",
        " hash sha",
        " authentication pre-share",
        " group 2",
        " lifetime 86400",
        "exit",
        f"crypto isakmp key {key} address {peer}",
        "crypto ipsec transform-set TS-WAN esp-aes esp-sha-hmac",
        "crypto map WANMAP 10 ipsec-isakmp",
        f" set peer {peer}",
        " set transform-set TS-WAN",
        f" match address {acl_num}",
        "exit",
    ]
    for l in local_nets:
        for r in remote_nets:
            lines.append(f"access-list {acl_num} permit ip {l.network_address} {l.hostmask} {r.network_address} {r.hostmask}")
    lines += [f"interface {iface}", " crypto map WANMAP", "exit"]
    return lines


SITE_NETS = {
    "HCM": ipaddress.ip_network("10.10.0.0/16"),
    "DBP": ipaddress.ip_network("10.20.0.0/16"),
    "BHTQ": ipaddress.ip_network("10.30.0.0/16"),
}

WAN_KEY = "HospitalWAN2026"


def wan_router_config(host):
    n = int(host[-1])
    site = "DBP" if n == 1 else "BHTQ"
    ckey = f"c{n}-wan{n}"
    lkey = f"wan{n}-{site.lower()}"
    lines = header(host) + loop_lines(host)
    lines += router_port("GigabitEthernet0/0", T.addr(ckey, 1), T.net(ckey), f"to CORE{n}")
    lines += router_port("GigabitEthernet0/1", T.addr(lkey, 0), T.net(lkey), f"leased line to {site}")
    other = "BHTQ" if site == "DBP" else "DBP"
    remote = [SITE_NETS[site]]
    local = [SITE_NETS["HCM"], SITE_NETS[other]]
    lines += crypto_lines(T.addr(lkey, 1), 110, local, remote, WAN_KEY, "GigabitEthernet0/1")
    lines += ospf_lines(host, [T.net(ckey), T.net(lkey)], ["GigabitEthernet0/0", "GigabitEthernet0/1"])
    return lines


def aux_router_config(site):
    host = f"R-{site}"
    n = 1 if site == "DBP" else 2
    lkey = f"wan{n}-{site.lower()}"
    subs = sorted([s for s in SUBNETS if s.site == site], key=lambda x: x.vlan)
    lines = header(host) + loop_lines(host)
    lines += router_port("GigabitEthernet0/0", T.addr(lkey, 1), T.net(lkey), f"leased line to R-WAN{n}")
    lines += ["interface GigabitEthernet0/1", " description trunk to switches", " no shutdown", "exit"]
    kinds = [acl_kind(s) for s in subs if acl_kind(s)]
    lines += acl_block(kinds, site)
    for s in subs:
        lines += [
            f"interface GigabitEthernet0/1.{s.vlan}",
            f" description {s.name}",
            f" encapsulation dot1Q {s.vlan}",
            f" ip address {s.gateway} {s.network.netmask}",
        ]
        kind = acl_kind(s)
        if kind:
            lines.append(f" ip access-group ACL-{kind.upper()} in")
        lines.append("exit")
    for s in subs:
        if is_dhcp(s):
            lines += dhcp_pool(s)
    remote = [v for k, v in SITE_NETS.items() if k != site]
    lines += crypto_lines(T.addr(lkey, 0), 110, [SITE_NETS[site]], remote, WAN_KEY, "GigabitEthernet0/0")
    lines += ospf_lines(host, [T.net(lkey)] + [s.network for s in subs], ["GigabitEthernet0/0"])
    return lines


def isp_config(name):
    if name == "ISP1":
        pub = T.PUBLIC["isp1-edge1"]
        up = T.PUBLIC["isp1-inet"]
        lines = header(name)
        lines += router_port("GigabitEthernet0/0", pub[1], ipaddress.ip_network(pub[0]), "to EDGE1")
        lines += router_port("GigabitEthernet0/1", up[1], ipaddress.ip_network(up[0]), "to INET")
        lines += [f"ip route 0.0.0.0 0.0.0.0 {up[2]}"]
        return lines
    pub = T.PUBLIC["isp2-edge2"]
    up = T.PUBLIC["isp2-inet"]
    tele = T.PUBLIC["tele-lan"]
    lines = header(name)
    lines += router_port("GigabitEthernet0/0", pub[1], ipaddress.ip_network(pub[0]), "to EDGE2")
    lines += router_port("GigabitEthernet0/1", up[1], ipaddress.ip_network(up[0]), "to INET")
    lines += router_port("GigabitEthernet0/2", tele[1], ipaddress.ip_network(tele[0]), "teleworker LAN")
    lines += [f"ip route 0.0.0.0 0.0.0.0 {up[2]}"]
    return lines


def inet_config():
    a = T.PUBLIC["isp1-inet"]
    b = T.PUBLIC["isp2-inet"]
    c = T.PUBLIC["inet-lan"]
    lines = header("INET")
    lines += router_port("GigabitEthernet0/0", a[2], ipaddress.ip_network(a[0]), "to ISP1")
    lines += router_port("GigabitEthernet0/1", b[2], ipaddress.ip_network(b[0]), "to ISP2")
    lines += router_port("GigabitEthernet0/2", c[1], ipaddress.ip_network(c[0]), "web server LAN")
    lines += [
        f"ip route {T.PUBLIC['isp1-edge1'][0].split('/')[0]} 255.255.255.248 {a[1]}",
        f"ip route {T.PUBLIC['isp2-edge2'][0].split('/')[0]} 255.255.255.248 {b[1]}",
        f"ip route {T.PUBLIC['tele-lan'][0].split('/')[0]} 255.255.255.0 {b[1]}",
    ]
    return lines


def edge_config(host):
    n = int(host[-1])
    pubkey = f"isp{n}-edge{n}"
    pub = T.PUBLIC[pubkey]
    pubnet = ipaddress.ip_network(pub[0])
    fkey = f"fw-e{n}"
    lines = header(host) + loop_lines(host)
    lines += router_port("GigabitEthernet0/0", pub[2], pubnet, f"to ISP{n}")
    lines += router_port("GigabitEthernet0/1", T.addr(fkey, 1), T.net(fkey), "to FW-HCM")
    lines += [
        "interface GigabitEthernet0/0",
        " ip nat outside",
        "exit",
        "interface GigabitEthernet0/1",
        " ip nat inside",
        "exit",
        "ip access-list extended NAT-SRC",
        f" deny ip 10.0.0.0 0.255.255.255 {T.VPN_NET} {T.VPN_WILD}",
        " permit ip 10.0.0.0 0.255.255.255 any",
        "exit",
        "ip nat inside source list NAT-SRC interface GigabitEthernet0/0 overload",
    ]
    base = ipaddress.ip_address(pub[2]) - 2
    for proto, inside, port, offset in T.STATIC_NAT:
        lines.append(f"ip nat inside source static {proto} {inside} {port} {base + offset} {port}")
    lines += [
        f"ip route 0.0.0.0 0.0.0.0 {pub[1]}",
        f"ip route 10.0.0.0 255.0.0.0 {T.addr(fkey, 0)}",
    ]
    if n == 1:
        lines += easy_vpn()
    return lines


def easy_vpn():
    return [
        "aaa new-model",
        "aaa authentication login default local",
        "aaa authentication login EZVPN-LOGIN local",
        "aaa authorization network EZVPN-GROUP local",
        "username teleuser secret Tele@2026",
        f"ip local pool TELE-POOL {T.VPN_POOL[0]} {T.VPN_POOL[1]}",
        "crypto isakmp policy 10",
        " encryption aes",
        " hash sha",
        " authentication pre-share",
        " group 2",
        "exit",
        "crypto isakmp client configuration group HOSPITAL-VPN",
        " key HospitalVPN2026",
        " pool TELE-POOL",
        "exit",
        "crypto ipsec transform-set TS-EZ esp-aes esp-sha-hmac",
        "crypto dynamic-map DYN 10",
        " set transform-set TS-EZ",
        " reverse-route",
        "exit",
        "crypto map EZMAP client authentication list EZVPN-LOGIN",
        "crypto map EZMAP isakmp authorization list EZVPN-GROUP",
        "crypto map EZMAP client configuration address respond",
        "crypto map EZMAP 65535 ipsec-isakmp dynamic DYN",
        "access-list 120 permit ip 10.10.36.64 0.0.0.15 " + f"{T.VPN_NET} {T.VPN_WILD}",
        "interface GigabitEthernet0/0",
        " crypto map EZMAP",
        "exit",
    ]


def fw_config():
    lines = [
        "hostname FW-HCM",
        f"enable password {ENABLE}",
        f"username admin password {ENABLE} privilege 15",
        "interface GigabitEthernet1/1",
        " nameif outside1",
        " security-level 0",
        f" ip address {T.addr('fw-e1', 0)} {T.net('fw-e1').netmask}",
        " no shutdown",
        "interface GigabitEthernet1/2",
        " nameif outside2",
        " security-level 0",
        f" ip address {T.addr('fw-e2', 0)} {T.net('fw-e2').netmask}",
        " no shutdown",
        "interface GigabitEthernet1/3",
        " nameif inside",
        " security-level 100",
        f" ip address {T.addr('fw-c1', 0)} {T.net('fw-c1').netmask}",
        " no shutdown",
        "interface GigabitEthernet1/4",
        " nameif dmz",
        " security-level 50",
        f" ip address {T.FW_DMZ_GW} 255.255.255.240",
        " no shutdown",
        "interface GigabitEthernet1/5",
        " nameif servers",
        " security-level 90",
        f" ip address {T.FW_SERVER_GW} 255.255.255.240",
        " no shutdown",
        f"route outside1 0.0.0.0 0.0.0.0 {T.addr('fw-e1', 1)} 1",
        f"route outside2 0.0.0.0 0.0.0.0 {T.addr('fw-e2', 1)} 1",
        f"route inside 10.0.0.0 255.0.0.0 {T.addr('fw-c1', 1)} 1",
        f"route outside1 {T.VPN_NET} 255.255.255.0 {T.addr('fw-e1', 1)} 1",
        "access-list OUT-IN extended permit icmp any any echo-reply",
        "access-list OUT-IN extended permit icmp any any unreachable",
        f"access-list OUT-IN extended permit tcp any host {T.DMZ_HOSTS['PORTAL']} eq www",
        f"access-list OUT-IN extended permit tcp any host {T.DMZ_HOSTS['PORTAL']} eq 443",
        f"access-list OUT-IN extended permit tcp any host {T.DMZ_HOSTS['MAIL-GW']} eq smtp",
        f"access-list OUT-IN extended permit tcp {T.VPN_NET} 255.255.255.0 host {T.SERVERS['HIS-APP']} eq 443",
        f"access-list OUT-IN extended permit icmp {T.VPN_NET} 255.255.255.0 10.10.36.64 255.255.255.240 echo",
        "access-list OUT-IN extended deny ip any any",
        "access-group OUT-IN in interface outside1",
        "access-group OUT-IN in interface outside2",
        f"access-list DMZ-IN extended permit tcp host {T.DMZ_HOSTS['PORTAL']} host {T.SERVERS['HIS-APP']} eq 8443",
        f"access-list DMZ-IN extended permit udp host {T.SERVERS['AD-DNS']} 10.10.36.80 255.255.255.240 eq domain",
        "access-list DMZ-IN extended deny ip 10.10.36.80 255.255.255.240 10.0.0.0 255.0.0.0",
        "access-list DMZ-IN extended permit tcp 10.10.36.80 255.255.255.240 any eq www",
        "access-list DMZ-IN extended permit tcp 10.10.36.80 255.255.255.240 any eq 443",
        "access-list DMZ-IN extended permit tcp 10.10.36.80 255.255.255.240 any eq smtp",
        "access-list DMZ-IN extended permit udp 10.10.36.80 255.255.255.240 any eq domain",
        "access-list DMZ-IN extended permit udp 10.10.36.80 255.255.255.240 any eq 123",
        "access-list DMZ-IN extended permit icmp 10.10.36.80 255.255.255.240 any",
        "access-list DMZ-IN extended deny ip any any",
        "access-group DMZ-IN in interface dmz",
        f"access-list SERVERS-IN extended permit udp host {T.SERVERS['NMS']} 10.0.0.0 255.0.0.0 eq snmp",
        f"access-list SERVERS-IN extended permit icmp host {T.SERVERS['NMS']} 10.0.0.0 255.0.0.0",
        "access-list SERVERS-IN extended permit tcp 10.10.36.64 255.255.255.240 any eq www",
        "access-list SERVERS-IN extended permit tcp 10.10.36.64 255.255.255.240 any eq 443",
        "access-list SERVERS-IN extended permit udp 10.10.36.64 255.255.255.240 any eq 123",
        "access-list SERVERS-IN extended permit icmp 10.10.36.64 255.255.255.240 any",
        "access-list SERVERS-IN extended deny ip any any",
        "access-group SERVERS-IN in interface servers",
    ]
    return lines


def device_configs():
    out = {}
    out["ISP1"] = isp_config("ISP1")
    out["ISP2"] = isp_config("ISP2")
    out["INET"] = inet_config()
    out["EDGE1"] = edge_config("EDGE1")
    out["EDGE2"] = edge_config("EDGE2")
    out["FW-HCM"] = fw_config()
    out["CORE1"] = core_config("CORE1")
    out["CORE2"] = core_config("CORE2")
    for ds in ("DS-A1", "DS-A2", "DS-B1", "DS-B2"):
        out[ds] = ds_config(ds)
    out["ACC-A"] = acc_config("ACC-A")
    out["ACC-B"] = acc_config("ACC-B")
    out["R-WAN1"] = wan_router_config("R-WAN1")
    out["R-WAN2"] = wan_router_config("R-WAN2")
    for site in ("DBP", "BHTQ"):
        out[f"R-{site}"] = aux_router_config(site)
        out[f"SW-{site}-1"] = aux_switch_config(site, 1)
        out[f"SW-{site}-2"] = aux_switch_config(site, 2)
    return out
