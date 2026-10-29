# 07 - Lệnh kiểm tra định tuyến và IPsec (nhóm 2)

Dùng sau khi nạp Configurations/*/02-routing.cfg. Chụp màn hình kết quả làm bằng chứng cho báo cáo và demo.

| Thiết bị | Lệnh | Kết quả mong đợi |
|---|---|---|
| ISP | show ip bgp summary | 3 neighbor ở trạng thái Established, mỗi neighbor gửi 1 prefix |
| ISP | show ip route bgp | 203.0.113.0/29, 198.51.100.0/29, 192.0.2.0/29 |
| HCM-R1, HN-R1, DN-R1 | show ip bgp summary | 1 neighbor Established, nhận 1 prefix (0.0.0.0/0) |
| HCM-R1, HN-R1, DN-R1 | show ip route 0.0.0.0 | route mặc định học bằng BGP (B*) |
| HCM-R1 | show crypto ikev2 sa | 2 SA ở trạng thái READY |
| HCM-R1 | show crypto ipsec sa | encaps và decaps tăng khi có ping |
| HCM-R1 | show interfaces tunnel 12 | up, up |
| HCM-R1 | show ip ospf neighbor | 4 neighbor FULL: CORE1, CORE2, HN-R1, DN-R1 |
| HCM-CORE1, CORE2 | show ip ospf neighbor | FULL với HCM-R1 |
| HCM-CORE1 | show ip route ospf | route 10.20.0.0/16 và 10.30.0.0/16 qua HCM-R1 (đi theo tunnel) |
| HN-SW1 | show ip route | route mặc định O*E2 từ HN-R1 |
| HCM-CORE1 | ping 10.20.255.11 source 10.10.255.11 | thành công, qua tunnel |
| HCM-CORE1 | traceroute 10.20.255.11 | đi qua HCM-R1 và địa chỉ 192.168.12.x, không qua ISP |

Việc cần thử khi demo failover: rút Gi0/1 của HCM-R1, dùng show ip ospf neighbor và ping liên tục để đo thời gian OSPF hội tụ sang CORE2.

Điểm cần kiểm chứng trên image thật (chưa thử trên máy nào): IKEv2 và tunnel protection có chạy trên IOSv, IOL hay không; lệnh ip tcp adjust-mss trên tunnel; thông báo cảnh báo của auto-cost reference-bandwidth.
