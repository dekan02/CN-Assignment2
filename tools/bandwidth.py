from dataclasses import dataclass

GROWTH = 1.2
PEAK_SHARE = 0.8
PEAK_SECONDS = 3 * 3600
MB_TO_MBIT = 8


def peak_mbps(mb_per_day):
    return mb_per_day * MB_TO_MBIT * PEAK_SHARE / PEAK_SECONDS


@dataclass
class Site:
    name: str
    workstations: int
    servers: int
    guest_devices: int
    pacs_studies_per_day: int = 0
    pacs_study_mb: int = 0
    his_users: int = 0


WS_DOWN, WS_UP = 500, 100
SRV_DOWN, SRV_UP = 1000, 2000
GUEST_DAILY = 500
HIS_MB_PER_USER_DAY = 40
CCTV_REMOTE_VIEW_MBPS = 8

SITES = [
    Site("HCM", 600, 10, 300),
    Site("DBP", 260, 2, 120, pacs_studies_per_day=60, pacs_study_mb=300, his_users=260),
    Site("BHTQ", 260, 2, 120, pacs_studies_per_day=60, pacs_study_mb=300, his_users=260),
]


def site_internet(site):
    down = peak_mbps(site.workstations * WS_DOWN + site.servers * SRV_DOWN + site.guest_devices * GUEST_DAILY)
    up = peak_mbps(site.workstations * WS_UP + site.servers * SRV_UP)
    return down, up


def site_intersite(site):
    if site.name == "HCM":
        return 0.0, 0.0
    pacs = peak_mbps(site.pacs_studies_per_day * site.pacs_study_mb)
    his = peak_mbps(site.his_users * HIS_MB_PER_USER_DAY)
    return his + CCTV_REMOTE_VIEW_MBPS, pacs + his


def rows():
    result = []
    for site in SITES:
        d, u = site_internet(site)
        sd, su = site_intersite(site)
        result.append({
            "site": site.name,
            "int_down": d,
            "int_up": u,
            "inter_down": sd,
            "inter_up": su,
        })
    return result


def summary():
    data = rows()
    main = data[0]
    aux = data[1:]
    internet_down = sum(r["int_down"] for r in data)
    internet_up = sum(r["int_up"] for r in data)
    wan = []
    for r in aux:
        down = r["int_down"] + r["inter_down"]
        up = r["int_up"] + r["inter_up"]
        wan.append({"site": r["site"], "down": down * GROWTH, "up": up * GROWTH})
    return {
        "per_site": data,
        "internet_down_now": internet_down,
        "internet_up_now": internet_up,
        "internet_down_5y": internet_down * GROWTH,
        "internet_up_5y": internet_up * GROWTH,
        "wan": wan,
        "main_lan_5y": (main["int_down"] + main["int_up"]) * GROWTH,
    }


def render():
    s = summary()
    lines = []
    lines.append("| Site | Internet xuống (Mbps) | Internet lên (Mbps) | Nội bộ về aux xuống (Mbps) | Nội bộ về aux lên (Mbps) |")
    lines.append("|---|---|---|---|---|")
    for r in s["per_site"]:
        lines.append(f"| {r['site']} | {r['int_down']:.1f} | {r['int_up']:.1f} | {r['inter_down']:.1f} | {r['inter_up']:.1f} |")
    lines.append("")
    lines.append(f"Tổng Internet hiện tại: xuống {s['internet_down_now']:.1f} Mbps, lên {s['internet_up_now']:.1f} Mbps")
    lines.append(f"Tổng Internet sau 5 năm (x{GROWTH}): xuống {s['internet_down_5y']:.1f} Mbps, lên {s['internet_up_5y']:.1f} Mbps")
    for w in s["wan"]:
        lines.append(f"Đường thuê riêng tới {w['site']} sau 5 năm: xuống {w['down']:.1f} Mbps, lên {w['up']:.1f} Mbps")
    return "\n".join(lines)


if __name__ == "__main__":
    print(render())
