# Assignment 2 - Checklist nộp bài

## Cấu trúc ZIP
TVI_Project_GroupXX/
- Report/TVI_Technical_Explanation_Report.pdf
- Configurations/HQ_Startup_Configs, Hanoi_Startup_Configs, DaNang_Startup_Configs
- Automation/inventory.yaml, auto_provision.py (hoặc deploy_baseline.yml), backups/

## Lab
- [ ] Hostname đúng convention
- [ ] Rapid PVST+/MSTP, root primary/secondary rõ ràng
- [ ] 802.1Q trunk, port không dùng vào VLAN 999 và shutdown
- [ ] LACP (mode active)
- [ ] IPv4 VLSM không overlap, IPv6 GUA trên interface dual-stack
- [ ] OSPF hội tụ, loopback reach được, passive-interface
- [ ] eBGP với ISP, iBGP, summarization ở chi nhánh
- [ ] Tunnel IPsec/EVPN UP/UP
- [ ] HSRP/VRRP preempt, priority 110
- [ ] DHCP relay hoạt động, DNS
- [ ] NAT overload
- [ ] ACL tách Corp/Guest/IoT; SSHv2, HTTPS, SNMPv3
- [ ] QoS: EF voice, AF31 video, policy trên WAN

## Automation
- [ ] Không password plaintext
- [ ] Inventory tách riêng
- [ ] try/except cho timeout và authentication
- [ ] Backup có timestamp vào backups/, log vào logs/automation.log
- [ ] Chạy lại không đổi thêm (idempotent)

## Báo cáo PDF
- [ ] Executive summary gắn với TVI
- [ ] Diagram rõ interface, subnet, VLAN, trust zone
- [ ] IP schema
- [ ] Rationale công nghệ
- [ ] Security, QoS, automation
- [ ] Ảnh CLI: show ip route, show ip bgp summary, ping, traceroute, failover
- [ ] TOC, số trang, một file PDF

## Demo
- [ ] 15 phút: end-to-end, failover dưới 3 phút, chạy script
- [ ] Giải thích được 100% code và config

## Khác
- [ ] Commit log liên tục trên repo
- [ ] Không trùng tên thiết bị/script với nhóm khác
