import ipaddress
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import bandwidth
import sizing
import configs
import topology as T
from model import SUBNETS, SITE_BLOCKS, GROUP_BLOCKS, GROWTH

GEN = os.path.join(ROOT, "docs", "generated")
CONF = os.path.join(ROOT, "Configurations")

WORKSTATION_VLANS = {
    "HCM": set(range(110, 116)) | set(range(210, 216)),
    "DBP": set(range(110, 114)),
    "BHTQ": set(range(110, 114)),
}
EXPECTED_WORKSTATIONS = {"HCM": 600, "DBP": 260, "BHTQ": 260}


def validate():
    problems = []
    nets = sorted(SUBNETS, key=lambda s: int(s.network.network_address))
    for a, b in zip(nets, nets[1:]):
        if a.network.overlaps(b.network):
            problems.append(f"overlap {a.name} {a.network} / {b.name} {b.network}")
    for s in SUBNETS:
        if not s.network.subnet_of(SITE_BLOCKS[s.site]):
            problems.append(f"{s.name} outside site block")
        usable = s.network.num_addresses - 2
        if usable < s.needed:
            problems.append(f"{s.name} too small: {usable} < {s.needed}")
    for site, expected in EXPECTED_WORKSTATIONS.items():
        total = sum(s.hosts for s in SUBNETS if s.site == site and s.vlan in WORKSTATION_VLANS[site])
        if total != expected:
            problems.append(f"{site} workstations {total} != {expected}")
    seen = {}
    for s in SUBNETS:
        key = (s.site, s.vlan)
        if key in seen:
            problems.append(f"duplicate vlan {key}")
        seen[key] = s.name
    infra = [v["network"] for v in T.LINKS.values()]
    for i, a in enumerate(infra):
        for b in infra[i + 1:]:
            if a.overlaps(b):
                problems.append(f"link overlap {a} {b}")
    for a in infra:
        for s in SUBNETS:
            if a.overlaps(s.network):
                problems.append(f"link {a} overlaps {s.name}")
    return problems


def ip_plan_md():
    lines = ["# Kế hoạch địa chỉ IP và VLAN", ""]
    lines.append(f"Sinh tự động bởi `tools/design.py`. Số host đã nhân hệ số tăng trưởng {GROWTH} và cộng 3 địa chỉ dự phòng cho gateway/HSRP.")
    lines.append("")
    for site, title in (("HCM", "Trụ sở chính TP.HCM"), ("DBP", "Chi nhánh đường DBP"), ("BHTQ", "Chi nhánh đường BHTQ")):
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| VLAN | Tên | Mô tả | Host hiện tại | Cần (có dự phòng) | Subnet | Gateway (VIP) | Dải host |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for s in sorted([x for x in SUBNETS if x.site == site], key=lambda x: int(x.network.network_address)):
            hosts = list(s.network.hosts())
            lines.append(f"| {s.vlan} | {s.name} | {s.description} | {s.hosts} | {s.needed} | {s.network} | {s.gateway} | {hosts[0]} - {hosts[-1]} |")
        total = sum(x.network.num_addresses for x in SUBNETS if x.site == site)
        block = SITE_BLOCKS[site].num_addresses
        lines.append("")
        lines.append(f"Đã dùng {total} / {block} địa chỉ của khối {SITE_BLOCKS[site]} ({100 * total / block:.1f}%).")
        lines.append("")
    return "\n".join(lines)


def links_md():
    lines = ["# Bảng liên kết point-to-point", "", "| Liên kết | Subnet | Đầu 1 | IP | Đầu 2 | IP |", "|---|---|---|---|---|---|"]
    for key, v in T.LINKS.items():
        lines.append(f"| {key} | {v['network']} | {v['first']} | {T.addr(key, 0)} | {v['second']} | {T.addr(key, 1)} |")
    lines.append("")
    lines.append("## Địa chỉ công cộng (mô phỏng Internet)")
    lines.append("")
    lines.append("| Liên kết | Subnet | IP đầu | IP cuối |")
    lines.append("|---|---|---|---|")
    for key, (net, a, b) in T.PUBLIC.items():
        lines.append(f"| {key} | {net} | {a} | {b} |")
    lines.append("")
    lines.append("## Static NAT tại EDGE")
    lines.append("")
    lines.append("| Giao thức | IP nội bộ | Cổng | IP công cộng EDGE1 | IP công cộng EDGE2 |")
    lines.append("|---|---|---|---|---|")
    e1 = ipaddress.ip_address(T.PUBLIC["isp1-edge1"][2]) - 2
    e2 = ipaddress.ip_address(T.PUBLIC["isp2-edge2"][2]) - 2
    for proto, inside, port, off in T.STATIC_NAT:
        lines.append(f"| {proto} | {inside} | {port} | {e1 + off} | {e2 + off} |")
    lines.append("")
    lines.append("## Server cố định")
    lines.append("")
    lines.append("| Tên | IP | Vùng |")
    lines.append("|---|---|---|")
    for n, a in T.SERVERS.items():
        lines.append(f"| {n} | {a} | Server farm |")
    for n, a in T.DMZ_HOSTS.items():
        lines.append(f"| {n} | {a} | DMZ |")
    lines.append("")
    lines.append("## Loopback (router-id)")
    lines.append("")
    from model import LOOPBACKS
    lines.append("| Thiết bị | Loopback0 |")
    lines.append("|---|---|")
    for n, a in LOOPBACKS.items():
        lines.append(f"| {n} | {a} |")
    return "\n".join(lines)


def wiring_md():
    lines = ["# Bảng đấu nối", "", "| # | Thiết bị 1 | Cổng | Thiết bị 2 | Cổng | Loại cáp |", "|---|---|---|---|---|---|"]
    for i, (a, pa, b, pb, kind) in enumerate(T.WIRING, 1):
        lines.append(f"| {i} | {a} | {pa} | {b} | {pb} | {kind} |")
    return "\n".join(lines)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.rstrip("\n") + "\n")


def main():
    problems = validate()
    if problems:
        for p in problems:
            print("LỖI:", p)
        sys.exit(1)
    write(os.path.join(GEN, "ip-plan.md"), ip_plan_md())
    write(os.path.join(GEN, "links.md"), links_md())
    write(os.path.join(GEN, "wiring.md"), wiring_md())
    write(os.path.join(GEN, "bandwidth.md"), "# Kết quả tính băng thông\n\n" + bandwidth.render())
    write(os.path.join(GEN, "sizing.md"), "# Kết quả tính số lượng thiết bị và uplink\n\n" + sizing.render())
    for name, lines in configs.device_configs().items():
        write(os.path.join(CONF, f"{name}.txt"), "\n".join(lines))
    print("OK", len(SUBNETS), "subnet,", len(T.LINKS), "link,", len(configs.device_configs()), "cấu hình")


if __name__ == "__main__":
    main()
