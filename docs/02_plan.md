# Assignment 2 - Kế hoạch thực hiện

Hôm nay: 27/10/2026. Deadline ghi trong đề: 17/11/2026 (còn 3 tuần, ít hơn 6 tuần trong đề, nên kế hoạch dưới đây được nén lại). Cần xác nhận lại deadline với giảng viên.

Cách làm: tự gõ config và code từng bước, nắm rõ làm gì và vì sao, chỉnh theo phong cách riêng (giống Assignment 1).

## Giai đoạn 0 - Việc phải chốt trước (27-28/10)

- [ ] Hỏi giảng viên các điểm mâu thuẫn ở file 01 mục 10 (deadline, nhóm/cá nhân, EVPN, nguồn image).
- [ ] Chốt nền tảng lab. Hướng đã chọn (bản nháp, chờ nhóm xác nhận):
  - Lab thật của nhóm: EVE-NG hoặc GNS3 trên máy x86 của đồng đội (cần RAM, số core, nested virtualization).
  - Luyện trên MacBook Apple Silicon: (1) FRR trong containerlab trên Docker Desktop cho OSPF/BGP/ISP, thư mục lab-frr/; (2) Packet Tracer cho VLAN, trunk, EtherChannel, OSPF, NAT, ACL, DHCP relay.
  - Không trích image IOL từ CML để chạy ngoài CML: giấy phép của Cisco chỉ cho dùng bên trong CML.
  - Phương án phụ: CML-Free trên máy x86 (giới hạn 5 node), hoặc license/lab server do trường cấp.
- [ ] Chốt nguồn image vIOS, vIOS-L2 (không được tải lậu; xem nguồn từ trường/CML).
- Kết quả nghiên cứu nền tảng lab: xem research/01_lab-platform.md
- [ ] Tạo repo GitHub/GitLab, commit ngay từ đầu (commit log là bằng chứng đóng góp).

## Giai đoạn 1 - Thiết kế (28/10 - 2/11) tương ứng Week 1, Step 1-2

- [ ] Đọc và ghi chú topic ở file 03.
- [ ] Vẽ logical topology bằng Draw.io: HCMC (core, 2 distribution, edge router, data center), Hanoi (router, 2 switch), Da Nang (router, 1 switch), ISP cloud, mgmt/automation node, trust zones (Corp, Guest, IoT, Mgmt).
- [ ] Quy hoạch VLAN: 10 Executive/Finance, 20 Engineering, 30 Logistics, 99 Management, Guest, IoT, Voice, 999 Blackhole.
- [ ] Quy hoạch IPv4 VLSM (sizing theo 4,000+ user, 10,000+ IoT, tăng trưởng 2030) và IPv6 phân cấp; làm bảng Excel/Markdown, kiểm tra không overlap và có thể summarize ở edge.
- [ ] Đặt tên thiết bị theo convention (HCMC-CORE-SW01, HANOI-RND-RTR01...), nhớ khác các nhóm khác.
- Đầu ra: diagram + IP plan để nộp duyệt.

## Giai đoạn 2 - Layer 2 và IP services (3-6/11) Week 2, Step 3-4

- [ ] Dựng topology trong lab, kiểm tra SSH từ automation node đến mọi thiết bị.
- [ ] VLAN, trunk 802.1Q, LACP, Rapid PVST+ với root primary/secondary.
- [ ] HSRP/VRRP (priority 110, preempt), SVI.
- [ ] DHCP tập trung ở HQ + DHCP relay ở chi nhánh, DNS.
- Kiểm tra: show spanning-tree, show etherchannel summary, show standby brief, client nhận IP qua relay.

## Giai đoạn 3 - Underlay routing (7-9/11) Week 3, Step 5

- [ ] OSPF (và OSPFv3 cho IPv6) trong từng site, passive-interface cho subnet user.
- [ ] Mọi Loopback0 reach được trong site.
- Kiểm tra: show ip ospf neighbor, show ip route ospf, ping loopback.

## Giai đoạn 4 - WAN, BGP, Security (9-13/11) Week 4, Step 6-7

- [ ] eBGP với ISP, iBGP giữa các site, summarization tại chi nhánh.
- [ ] Nối site: IPsec VPN (khả thi trên vIOS) hoặc EVPN nếu có image phù hợp.
- [ ] NAT overload tại edge.
- [ ] ACL Guest/IoT/Corp, DHCP Snooping, DAI, Port Security, SSHv2 thay Telnet.
- Kiểm tra: show ip bgp summary, tunnel UP/UP, kiểm tra ACL chặn đúng.

## Giai đoạn 5 - QoS và Automation (12-15/11) Week 5, Step 8-9

- [ ] QoS: class-map/policy-map, EF cho voice, AF31 cho video, áp lên WAN interface; tạo traffic giả để chứng minh.
- [ ] Automation (Python Netmiko hoặc Ansible): inventory ngoài, credential qua getpass/env, push baseline + VLAN, backup trước/sau, log lỗi SSH. Tự viết, không dán nguyên starter code (phải giải thích 100%).
- Kiểm tra: chạy lặp lại không đổi thêm (idempotent), một node chết không làm crash script.

## Giai đoạn 6 - Test, báo cáo, demo (14-17/11) Week 6, Step 10

- [ ] Test end-to-end, traceroute, failover (shutdown core link, hội tụ dưới 3 phút); chụp CLI làm bằng chứng.
- [ ] Export startup-config tất cả thiết bị.
- [ ] Viết Technical Report PDF (TOC, số trang, executive summary, diagrams, IP schema, rationale, security/QoS/automation, testing).
- [ ] Đóng gói theo cấu trúc: TVI_Project_GroupXX/Report, Configurations (HQ/Hanoi/DaNang), Automation (inventory.yaml, script, backups).
- [ ] Tập demo 15 phút, dự phòng khi lab lỗi (video quay sẵn).
- [ ] Luyện giải thích mọi dòng config và code cho phần oral defense.

## Rủi ro chính

| Rủi ro | Giảm thiểu |
|---|---|
| Mac ARM không chạy được image Cisco | Luyện bằng FRR và Packet Tracer trên Mac; lab thật chạy trên máy x86 của nhóm |
| Thiếu image vIOS | Xin từ trường hoặc dùng CML |
| Lab quá nặng (RAM) | Bật node theo batch 3-5, giảm node không cần thiết |
| Thiếu thời gian (3 tuần thay vì 6) | Ưu tiên Step có điểm và dễ chứng minh, EVPN để ở mức thiết kế nếu image không hỗ trợ |
| Demo failover không lặp lại được | Tập trước nhiều lần, lưu trạng thái lab |
