# 06 - Phân chia việc (nhóm 2 người)

Chia theo 5 nhóm của đề, ghép vào cuối tuần. Bản nháp, chờ nhóm xác nhận.

| Nhóm | Nội dung | Người làm |
|---|---|---|
| 1 | Layer 2 (VLAN, trunk, LACP, STP), HSRP, DHCP relay | Đồng đội |
| 2 | OSPF, BGP, IPsec | Khang |
| 3 | NAT, ACL, DHCP Snooping, DAI, QoS | Đồng đội |
| 4 | Script Netmiko và kế hoạch IP | Khang |
| 5 | Báo cáo PDF, đóng gói ZIP | Chia đôi: mỗi người viết phần của mình, một người gom |

## Việc của nhóm 2 (OSPF, BGP, IPsec)

1. BGP: lab FRR đã chạy, ISP học đủ 3 prefix. Còn lại: viết cấu hình tương đương bằng lệnh Cisco IOS cho 3 edge router để dùng trong lab thật.
2. OSPF: thêm OSPF area 0 vào lab FRR (loopback và link nội bộ), kiểm tra route học qua OSPF.
3. IPsec VTI IKEv2 giữa HCM-R1 và HN-R1, HCM-R1 và DN-R1: viết cấu hình mẫu, rồi thử trên Packet Tracer hoặc lab x86 của nhóm (FRR không làm IPsec Cisco).
4. Ghi lại mỗi cấu hình kèm lệnh kiểm tra (show ip bgp summary, show ip ospf neighbor, show crypto ipsec sa) làm bằng chứng cho báo cáo và demo.

## Việc của nhóm 4 (Netmiko và kế hoạch IP)

1. Bảng IP và VLAN: lấy từ 05_topology-design.md, kiểm tra không trùng dải, thêm phần IPv6, chốt với đồng đội.
2. Inventory YAML: danh sách thiết bị, IP quản trị, vai trò.
3. Script Netmiko: đọc inventory, kết nối SSH, đẩy cấu hình từ file mẫu, chạy lại nhiều lần không phá cấu hình (so sánh trước khi gửi).
4. Thử script trên lab FRR ở Mac (FRR có SSH hạn chế nên có thể thử bằng container Linux), rồi trên lab thật khi nhóm dựng xong.

## Hạn chung

- Trước cuối tuần: chốt nền tảng lab và cấu hình máy x86 của đồng đội.
- Cuối tuần: gộp cấu hình, chạy thử toàn bộ, tập demo failover.

## Tiến độ nhóm 2 và 4 (29/10/2026)

- Nhóm 2: đã viết Configurations/*/02-routing.cfg cho ISP, 3 edge router, HCM-CORE1, HCM-CORE2, HN-SW1 (OSPF area 0, eBGP với ISP, IPsec VTI IKEv2). Chưa thử trên thiết bị thật. Lệnh kiểm tra ở docs/07.
- Nhóm 4: đã có Automation/ip-plan.yml, check_plan.py, deploy.py, inventory.yml, unit test. Chưa kết nối thiết bị thật nên phần Netmiko chưa được chạy với lab.
