import math
from model import SUBNETS, GROWTH
import bandwidth as bw

PORT_SPARE = 1.2
SWITCH_PORTS = 48
ACCESS_OVERSUB = 20
DIST_OVERSUB = 4
CCTV_MBPS = 4
SERVER_FARM_MBPS_PER_WS = 1.0
PACS_STUDIES_MAIN = 200
PACS_STUDY_MB = 400


def count(site, group, suffixes, workstation_vlans):
    ws = sum(s.hosts for s in SUBNETS if s.site == site and s.group == group and s.vlan in workstation_vlans)
    extra = {}
    for tag in suffixes:
        extra[tag] = sum(s.hosts for s in SUBNETS if s.site == site and s.group == group and s.name.endswith(tag))
    return ws, extra


def building(site, group, ws_vlans):
    ws, extra = count(site, group, ("AP", "CCTV", "MEDDEV"), ws_vlans)
    ports = ws + sum(extra.values())
    ports_spare = math.ceil(ports * PORT_SPARE)
    switches = math.ceil(ports_spare / SWITCH_PORTS)
    return {
        "site": site,
        "group": group,
        "workstations": ws,
        "ap": extra["AP"],
        "cctv": extra["CCTV"],
        "meddev": extra["MEDDEV"],
        "ports": ports,
        "ports_spare": ports_spare,
        "switches": switches,
    }


def report():
    rows = [
        building("HCM", "A", set(range(110, 116))),
        building("HCM", "B", set(range(210, 216))),
        building("DBP", "S", set(range(110, 114))),
        building("BHTQ", "S", set(range(110, 114))),
    ]
    for r in rows:
        r["uplink_need_gbps"] = SWITCH_PORTS / ACCESS_OVERSUB
        r["dist_down_gbps"] = r["switches"] * 10
        r["dist_to_core_gbps"] = r["dist_down_gbps"] / DIST_OVERSUB
    main_ws = sum(r["workstations"] for r in rows[:2])
    cctv_main = sum(r["cctv"] for r in rows[:2])
    cctv_stream = cctv_main * CCTV_MBPS
    server_farm = main_ws * SERVER_FARM_MBPS_PER_WS * GROWTH
    pacs = bw.peak_mbps(PACS_STUDIES_MAIN * PACS_STUDY_MB) * GROWTH
    summary = bw.summary()
    internet = summary["internet_down_5y"] + summary["internet_up_5y"]
    fw_total = internet + server_farm + cctv_stream * GROWTH + pacs
    return {
        "rows": rows,
        "cctv_stream_mbps": cctv_stream,
        "server_farm_mbps": server_farm,
        "pacs_mbps": pacs,
        "internet_mbps": internet,
        "fw_total_mbps": fw_total,
    }


def render():
    r = report()
    lines = ["| Khu vực | Máy trạm | AP | Camera | TB y tế | Cổng cần | Cổng + 20% dự phòng | Switch 48 cổng |", "|---|---|---|---|---|---|---|---|"]
    names = {("HCM", "A"): "Tòa A", ("HCM", "B"): "Tòa B", ("DBP", "S"): "DBP", ("BHTQ", "S"): "BHTQ"}
    for x in r["rows"]:
        lines.append(f"| {names[(x['site'], x['group'])]} | {x['workstations']} | {x['ap']} | {x['cctv']} | {x['meddev']} | {x['ports']} | {x['ports_spare']} | {x['switches']} |")
    lines.append("")
    lines.append(f"Uplink mỗi switch access: tối thiểu {SWITCH_PORTS / ACCESS_OVERSUB:.1f} Gbps (oversubscription {ACCESS_OVERSUB}:1) nên dùng 1 x 10G tới mỗi distribution.")
    for x in r["rows"][:2]:
        lines.append(f"Distribution tòa {x['group']}: {x['switches']} x 10G xuống access = {x['dist_down_gbps']} Gbps, lên core tối thiểu {x['dist_to_core_gbps']:.1f} Gbps (oversubscription {DIST_OVERSUB}:1) nên dùng 2 x 40G.")
    lines.append("")
    lines.append(f"Luồng camera trụ sở: {r['cctv_stream_mbps']:.0f} Mbps liên tục ({CCTV_MBPS} Mbps/camera).")
    lines.append(f"Luồng máy trạm tới server farm (giả định {SERVER_FARM_MBPS_PER_WS} Mbps/máy lúc cao điểm, đã tăng trưởng): {r['server_farm_mbps']:.0f} Mbps.")
    lines.append(f"PACS trụ sở ({PACS_STUDIES_MAIN} ca/ngày x {PACS_STUDY_MB} MB): {r['pacs_mbps']:.0f} Mbps cao điểm.")
    lines.append(f"Lưu lượng Internet sau 5 năm: {r['internet_mbps']:.0f} Mbps (hai chiều).")
    lines.append(f"Tổng lưu lượng đi qua firewall (ước tính): {r['fw_total_mbps']:.0f} Mbps, nên chọn NGFW có throughput bật IPS tối thiểu {math.ceil(r['fw_total_mbps'] * 2 / 1000)} Gbps (hệ số an toàn 2).")
    return "\n".join(lines)


if __name__ == "__main__":
    print(render())
