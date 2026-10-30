from model import LinkPool, subnet, loopback

SEC = LinkPool("172.16.0.0/24")
WAN = LinkPool("172.16.1.0/24")
LA = LinkPool("172.16.2.0/24")
LB = LinkPool("172.16.3.0/24")

LINKS = {}


def link(key, pool, first, second):
    LINKS[key] = pool.take(key, first, second)


link("fw-e1", SEC, "FW-HCM", "EDGE1")
link("fw-e2", SEC, "FW-HCM", "EDGE2")
link("fw-c1", SEC, "FW-HCM", "CORE1")
link("core-core", SEC, "CORE1", "CORE2")
link("c1-wan1", WAN, "CORE1", "R-WAN1")
link("c2-wan2", WAN, "CORE2", "R-WAN2")
link("wan1-dbp", WAN, "R-WAN1", "R-DBP")
link("wan2-bhtq", WAN, "R-WAN2", "R-BHTQ")
for ds in ("DS-A1", "DS-A2"):
    for core in ("CORE1", "CORE2"):
        link(f"{ds}-{core}", LA, ds, core)
for ds in ("DS-B1", "DS-B2"):
    for core in ("CORE1", "CORE2"):
        link(f"{ds}-{core}", LB, ds, core)


def addr(key, side):
    return LINKS[key]["network"].network_address + 1 + side


def net(key):
    return LINKS[key]["network"]


for name in ("CORE1", "CORE2", "DS-A1", "DS-A2", "DS-B1", "DS-B2", "R-WAN1", "R-WAN2", "R-DBP", "R-BHTQ", "FW-HCM", "EDGE1", "EDGE2"):
    loopback(name)

PUBLIC = {
    "isp1-edge1": ("203.0.113.0/29", "203.0.113.1", "203.0.113.2"),
    "isp2-edge2": ("198.51.100.0/29", "198.51.100.1", "198.51.100.2"),
    "isp1-inet": ("100.64.1.0/30", "100.64.1.1", "100.64.1.2"),
    "isp2-inet": ("100.64.2.0/30", "100.64.2.1", "100.64.2.2"),
    "inet-lan": ("192.0.2.0/24", "192.0.2.1", "192.0.2.10"),
    "tele-lan": ("198.51.101.0/24", "198.51.101.1", "198.51.101.10"),
}

SERVERS = {
    "HIS-APP": "10.10.36.66",
    "HIS-DB": "10.10.36.67",
    "PACS": "10.10.36.68",
    "LIS": "10.10.36.69",
    "AD-DNS": "10.10.36.70",
    "FILE": "10.10.36.71",
    "NMS": "10.10.36.72",
    "NVR": "10.10.36.73",
    "BACKUP": "10.10.36.74",
}

DMZ_HOSTS = {
    "PORTAL": "10.10.36.82",
    "MAIL-GW": "10.10.36.83",
    "VPN-PROXY": "10.10.36.84",
}

STATIC_NAT = [
    ("tcp", "10.10.36.82", 80, 3),
    ("tcp", "10.10.36.82", 443, 3),
    ("tcp", "10.10.36.83", 25, 4),
]

VPN_POOL = ("192.168.99.10", "192.168.99.60")
VPN_NET = "192.168.99.0"
VPN_WILD = "0.0.0.255"

WLC_MGMT = "10.10.36.4"
FW_SERVER_GW = "10.10.36.65"
FW_DMZ_GW = "10.10.36.81"


WIRING = [
    ("ISP1", "Gi0/0", "EDGE1", "Gi0/0", "Đồng thẳng"),
    ("ISP1", "Gi0/1", "INET", "Gi0/0", "Đồng thẳng"),
    ("ISP2", "Gi0/0", "EDGE2", "Gi0/0", "Đồng thẳng"),
    ("ISP2", "Gi0/1", "INET", "Gi0/1", "Đồng thẳng"),
    ("ISP2", "Gi0/2", "TELE-PC", "Fa0", "Đồng chéo"),
    ("INET", "Gi0/2", "WEB-INET", "Fa0", "Đồng chéo"),
    ("EDGE1", "Gi0/1", "FW-HCM", "Gi1/1", "Đồng chéo"),
    ("EDGE2", "Gi0/1", "FW-HCM", "Gi1/2", "Đồng chéo"),
    ("FW-HCM", "Gi1/3", "CORE1", "Gi1/0/1", "Đồng chéo"),
    ("FW-HCM", "Gi1/4", "SW-DMZ", "Gi0/1", "Đồng thẳng"),
    ("FW-HCM", "Gi1/5", "SW-SRV", "Gi0/1", "Đồng thẳng"),
    ("SW-DMZ", "Fa0/1", "PORTAL", "Fa0", "Đồng thẳng"),
    ("SW-DMZ", "Fa0/2", "MAIL-GW", "Fa0", "Đồng thẳng"),
    ("SW-SRV", "Fa0/1", "HIS-APP", "Fa0", "Đồng thẳng"),
    ("SW-SRV", "Fa0/2", "PACS", "Fa0", "Đồng thẳng"),
    ("SW-SRV", "Fa0/3", "AD-DNS", "Fa0", "Đồng thẳng"),
    ("SW-SRV", "Fa0/4", "NMS", "Fa0", "Đồng thẳng"),
    ("SW-SRV", "Fa0/5", "NVR", "Fa0", "Đồng thẳng"),
    ("CORE1", "Gi1/0/2", "CORE2", "Gi1/0/2", "Đồng chéo"),
    ("CORE1", "Gi1/0/3", "DS-A1", "Gi1/0/1", "Đồng chéo"),
    ("CORE2", "Gi1/0/3", "DS-A1", "Gi1/0/2", "Đồng chéo"),
    ("CORE1", "Gi1/0/4", "DS-A2", "Gi1/0/1", "Đồng chéo"),
    ("CORE2", "Gi1/0/4", "DS-A2", "Gi1/0/2", "Đồng chéo"),
    ("CORE1", "Gi1/0/5", "DS-B1", "Gi1/0/1", "Đồng chéo"),
    ("CORE2", "Gi1/0/5", "DS-B1", "Gi1/0/2", "Đồng chéo"),
    ("CORE1", "Gi1/0/6", "DS-B2", "Gi1/0/1", "Đồng chéo"),
    ("CORE2", "Gi1/0/6", "DS-B2", "Gi1/0/2", "Đồng chéo"),
    ("CORE1", "Gi1/0/7", "R-WAN1", "Gi0/0", "Đồng chéo"),
    ("CORE2", "Gi1/0/7", "R-WAN2", "Gi0/0", "Đồng chéo"),
    ("CORE1", "Gi1/0/8", "WLC", "Port 1", "Đồng thẳng"),
    ("R-WAN1", "Gi0/1", "R-DBP", "Gi0/0", "Đồng chéo"),
    ("R-WAN2", "Gi0/1", "R-BHTQ", "Gi0/0", "Đồng chéo"),
    ("DS-A1", "Gi1/0/3", "ACC-A", "Gi0/1", "Đồng chéo"),
    ("DS-A2", "Gi1/0/3", "ACC-A", "Gi0/2", "Đồng chéo"),
    ("DS-A1", "Gi1/0/4", "DS-A2", "Gi1/0/4", "Đồng chéo"),
    ("DS-B1", "Gi1/0/3", "ACC-B", "Gi0/1", "Đồng chéo"),
    ("DS-B2", "Gi1/0/3", "ACC-B", "Gi0/2", "Đồng chéo"),
    ("DS-B1", "Gi1/0/4", "DS-B2", "Gi1/0/4", "Đồng chéo"),
    ("ACC-A", "Fa0/1", "PC-A-RECEPTION", "Fa0", "Đồng thẳng"),
    ("ACC-A", "Fa0/2", "PC-A-PHARMACY", "Fa0", "Đồng thẳng"),
    ("ACC-A", "Fa0/3", "PC-A-OUTPATIENT-1", "Fa0", "Đồng thẳng"),
    ("ACC-A", "Fa0/4", "PC-A-LAB", "Fa0", "Đồng thẳng"),
    ("ACC-A", "Fa0/5", "PC-A-IMAGING", "Fa0", "Đồng thẳng"),
    ("ACC-A", "Fa0/6", "PC-A-SURGERY", "Fa0", "Đồng thẳng"),
    ("ACC-A", "Fa0/7", "AP-A", "Port 0", "Đồng thẳng"),
    ("ACC-A", "Fa0/8", "CAM-A", "Fa0", "Đồng thẳng"),
    ("ACC-A", "Fa0/9", "MED-A", "Fa0", "Đồng thẳng"),
    ("ACC-A", "Fa0/10", "PHONE-A", "Fa0", "Đồng thẳng"),
    ("ACC-A", "Fa0/11", "PC-A-OUTPATIENT-2", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/1", "PC-B-ER", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/2", "PC-B-INPATIENT-1", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/3", "PC-B-ADMIN", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/4", "PC-B-FINANCE", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/5", "PC-B-TRAINING", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/6", "PC-B-IT", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/7", "AP-B", "Port 0", "Đồng thẳng"),
    ("ACC-B", "Fa0/8", "CAM-B", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/9", "MED-B", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/10", "PHONE-B", "Fa0", "Đồng thẳng"),
    ("ACC-B", "Fa0/11", "PC-B-INPATIENT-2", "Fa0", "Đồng thẳng"),
]

for _site in ("DBP", "BHTQ"):
    WIRING += [
        (f"R-{_site}", "Gi0/1", f"SW-{_site}-1", "Gi0/1", "Đồng chéo"),
        (f"SW-{_site}-1", "Gi0/2", f"SW-{_site}-2", "Gi0/1", "Đồng chéo"),
        (f"SW-{_site}-1", "Fa0/1", f"PC-{_site}-CLINIC-1", "Fa0", "Đồng thẳng"),
        (f"SW-{_site}-1", "Fa0/2", f"PC-{_site}-LABIMG", "Fa0", "Đồng thẳng"),
        (f"SW-{_site}-1", "Fa0/3", f"AP-{_site}-1", "Port 0", "Đồng thẳng"),
        (f"SW-{_site}-1", "Fa0/4", f"CAM-{_site}", "Fa0", "Đồng thẳng"),
        (f"SW-{_site}-1", "Fa0/5", f"PHONE-{_site}", "Fa0", "Đồng thẳng"),
        (f"SW-{_site}-1", "Fa0/6", f"PC-{_site}-CLINIC-2", "Fa0", "Đồng thẳng"),
        (f"SW-{_site}-2", "Fa0/1", f"PC-{_site}-ADMIN", "Fa0", "Đồng thẳng"),
        (f"SW-{_site}-2", "Fa0/2", f"PC-{_site}-IT", "Fa0", "Đồng thẳng"),
        (f"SW-{_site}-2", "Fa0/3", f"MED-{_site}", "Fa0", "Đồng thẳng"),
        (f"SW-{_site}-2", "Fa0/4", f"SRV-{_site}", "Fa0", "Đồng thẳng"),
        (f"SW-{_site}-2", "Fa0/5", f"AP-{_site}-2", "Port 0", "Đồng thẳng"),
    ]
