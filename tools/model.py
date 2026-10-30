import ipaddress
import math
from dataclasses import dataclass

GROWTH = 1.2
RESERVED_HOSTS = 3


@dataclass
class Subnet:
    name: str
    vlan: int
    site: str
    group: str
    description: str
    hosts: int
    network: ipaddress.IPv4Network = None

    @property
    def gateway(self):
        return self.network.network_address + 1

    @property
    def gateway_a(self):
        return self.network.network_address + 2

    @property
    def gateway_b(self):
        return self.network.network_address + 3

    def host(self, offset):
        return self.network.network_address + offset

    @property
    def needed(self):
        return math.ceil(self.hosts * GROWTH) + RESERVED_HOSTS

    @property
    def prefix(self):
        bits = max(2, (self.needed + 1).bit_length())
        return 32 - bits


SITE_BLOCKS = {
    "HCM": ipaddress.ip_network("10.10.0.0/16"),
    "DBP": ipaddress.ip_network("10.20.0.0/16"),
    "BHTQ": ipaddress.ip_network("10.30.0.0/16"),
}

GROUP_BLOCKS = {
    ("HCM", "A"): ipaddress.ip_network("10.10.0.0/20"),
    ("HCM", "B"): ipaddress.ip_network("10.10.16.0/20"),
    ("HCM", "S"): ipaddress.ip_network("10.10.32.0/20"),
    ("DBP", "S"): ipaddress.ip_network("10.20.0.0/20"),
    ("BHTQ", "S"): ipaddress.ip_network("10.30.0.0/20"),
}

DEFINITIONS = [
    ("HCM", "A", 110, "A-RECEPTION", "Tiếp đón, thu ngân (tầng 1 tòa A)", 50),
    ("HCM", "A", 111, "A-PHARMACY", "Nhà thuốc (tầng 1 tòa A)", 30),
    ("HCM", "A", 112, "A-OUTPATIENT", "Khám bệnh ngoại trú (tầng 2 tòa A)", 90),
    ("HCM", "A", 113, "A-LAB", "Xét nghiệm (tầng 3 tòa A)", 40),
    ("HCM", "A", 114, "A-IMAGING", "Chẩn đoán hình ảnh (tầng 4 tòa A)", 50),
    ("HCM", "A", 115, "A-SURGERY", "Phẫu thuật, gây mê hồi sức (tầng 5 tòa A)", 30),
    ("HCM", "A", 150, "A-VOICE", "Điện thoại IP tòa A", 200),
    ("HCM", "A", 160, "A-MEDDEV", "Thiết bị y tế tòa A", 120),
    ("HCM", "A", 170, "A-AP", "Access point tòa A", 30),
    ("HCM", "A", 180, "A-CCTV", "Camera tòa A", 46),
    ("HCM", "A", 199, "A-MGMT", "Quản trị thiết bị tòa A", 40),
    ("HCM", "B", 210, "B-ER", "Cấp cứu, hồi sức (tầng 1 tòa B)", 40),
    ("HCM", "B", 211, "B-INPATIENT", "Nội trú (tầng 2 và 3 tòa B)", 110),
    ("HCM", "B", 212, "B-ADMIN", "Ban giám đốc, hành chính (tầng 4 tòa B)", 70),
    ("HCM", "B", 213, "B-FINANCE-HR", "Tài chính, kế toán, nhân sự (tầng 5 tòa B)", 40),
    ("HCM", "B", 214, "B-TRAINING", "Đào tạo, nghiên cứu (tầng 5 tòa B)", 30),
    ("HCM", "B", 215, "B-IT", "Phòng IT (tầng 5 tòa B)", 20),
    ("HCM", "B", 250, "B-VOICE", "Điện thoại IP tòa B", 200),
    ("HCM", "B", 260, "B-MEDDEV", "Thiết bị y tế tòa B", 120),
    ("HCM", "B", 270, "B-AP", "Access point tòa B", 30),
    ("HCM", "B", 280, "B-CCTV", "Camera tòa B", 46),
    ("HCM", "B", 299, "B-MGMT", "Quản trị thiết bị tòa B", 40),
    ("HCM", "S", 300, "SERVER", "Server farm (7 server và 2 thiết bị lưu trữ)", 9),
    ("HCM", "S", 310, "DMZ", "DMZ (portal, mail gateway, VPN)", 3),
    ("HCM", "S", 320, "WIFI-STAFF", "WiFi nhân viên (802.1X)", 250),
    ("HCM", "S", 330, "WIFI-GUEST", "WiFi khách và bệnh nhân (cách ly)", 300),
    ("HCM", "S", 399, "CORE-MGMT", "Quản trị lõi, tường lửa, WLC, IPS, giám sát", 30),
]

for _site, _label in (("DBP", "DBP"), ("BHTQ", "BHTQ")):
    DEFINITIONS += [
        (_site, "S", 110, f"{_label}-CLINIC", "Khám bệnh (tầng 1 và 2)", 120),
        (_site, "S", 111, f"{_label}-LABIMG", "Xét nghiệm, chẩn đoán hình ảnh", 60),
        (_site, "S", 112, f"{_label}-ADMIN", "Hành chính, thu ngân, nhà thuốc", 60),
        (_site, "S", 113, f"{_label}-IT", "Phòng IT", 20),
        (_site, "S", 150, f"{_label}-VOICE", "Điện thoại IP", 120),
        (_site, "S", 160, f"{_label}-MEDDEV", "Thiết bị y tế", 40),
        (_site, "S", 170, f"{_label}-AP", "Access point", 14),
        (_site, "S", 180, f"{_label}-CCTV", "Camera", 26),
        (_site, "S", 300, f"{_label}-SERVER", "Server cục bộ", 2),
        (_site, "S", 320, f"{_label}-WIFI-STAFF", "WiFi nhân viên", 80),
        (_site, "S", 330, f"{_label}-WIFI-GUEST", "WiFi khách (cách ly)", 120),
        (_site, "S", 399, f"{_label}-MGMT", "Quản trị thiết bị", 20),
    ]


def allocate_subnets():
    subnets = [Subnet(name, vlan, site, group, desc, hosts) for site, group, vlan, name, desc, hosts in DEFINITIONS]
    groups = {}
    for subnet in subnets:
        groups.setdefault((subnet.site, subnet.group), []).append(subnet)
    for key, members in groups.items():
        block = GROUP_BLOCKS[key]
        cursor = int(block.network_address)
        end = int(block.broadcast_address)
        for subnet in sorted(members, key=lambda item: (item.prefix, item.vlan)):
            size = 2 ** (32 - subnet.prefix)
            if cursor % size:
                cursor += size - cursor % size
            if cursor + size - 1 > end:
                raise ValueError(f"block {block} is full at {subnet.name}")
            subnet.network = ipaddress.ip_network((cursor, subnet.prefix))
            cursor += size
    return subnets


SUBNETS = allocate_subnets()
BY_NAME = {subnet.name: subnet for subnet in SUBNETS}


def subnet(name):
    return BY_NAME[name]


class LinkPool:
    def __init__(self, block):
        self.block = ipaddress.ip_network(block)
        self.cursor = int(self.block.network_address)
        self.links = []

    def take(self, label, first, second):
        network = ipaddress.ip_network((self.cursor, 30))
        self.cursor += 4
        entry = {"label": label, "network": network, "first": first, "second": second}
        self.links.append(entry)
        return entry


INFRA = LinkPool("172.16.0.0/16")
LOOPBACKS = {}


def loopback(name):
    if name not in LOOPBACKS:
        LOOPBACKS[name] = ipaddress.ip_address(int(ipaddress.ip_address("172.16.255.0")) + len(LOOPBACKS) + 1)
    return LOOPBACKS[name]
