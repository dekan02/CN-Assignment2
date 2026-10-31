# 05 - Dựng mô phỏng và kiểm thử (Bước 4 và 5)

Phiên bản đã cài: Packet Tracer 8.2.2 và 9.0.1. Cấu hình của mọi thiết bị nằm trong thư mục `Configurations/`, sinh từ `tools/design.py`. Thư mục này chứa lệnh IOS/ASA thuần, dán vào CLI từng thiết bị theo thứ tự dưới đây.

## 1. Tính năng chưa kiểm chứng trong Packet Tracer

Những điểm này chưa thể kiểm tra từ môi trường soạn tài liệu, phải thử trực tiếp trên máy có Packet Tracer; mỗi mục có phương án thay thế.

| Tính năng | Rủi ro | Phương án thay thế |
|---|---|---|
| HSRP (`standby`) trên Catalyst 3650-24PS | Có thể không hỗ trợ | Đổi sang 3560-24PS, thêm `switchport trunk encapsulation dot1q` trước `switchport mode trunk` |
| ASA 5506-X: hai route mặc định bằng nhau qua hai giao diện (ECMP) | Có thể chỉ dùng một route | Giữ một route mặc định qua EDGE1; chia tải chứng minh bằng cách ép lưu lượng từ nửa số VLAN qua EDGE2 trên core |
| IPsec trên Cisco 2911 | Cần gói security | Nhập `license boot module c2900 technology-package securityk9`, xác nhận `yes`, `write memory`, `reload` |
| Easy VPN và VPN client trên PC | Có thể không có | Chỉ trình bày trong báo cáo và dùng site-to-site IPsec làm bằng chứng |
| WLC và LAP | Cách LAP tìm WLC có thể khác | Dùng AP độc lập (AccessPoint-PT) với hai SSID, VLAN gắn trên cổng switch |
| Chuyển đổi dự phòng tự động khi nhà mạng hỏng | Cần IP SLA/track | Mô phỏng bằng cách `shutdown` cổng EDGE1 Gi0/1 |
| IPS/IDS, lọc URL, phát hiện phishing | Packet Tracer không mô phỏng | Chỉ trình bày trong thiết kế và báo cáo |
| GPON | Không có OLT/ONT như đề | Chỉ trình bày trong thiết kế |

## 2. Thiết bị cần thả vào workspace

| Nhóm | Thiết bị |
|---|---|
| Internet | ISP1, ISP2, INET (router 2911); WEB-INET, TELE-PC |
| Biên | EDGE1, EDGE2 (2911); FW-HCM (ASA 5506-X) |
| Lõi và tòa nhà | CORE1, CORE2, DS-A1, DS-A2, DS-B1, DS-B2 (3650-24PS); ACC-A, ACC-B (2960-24TT) |
| Dịch vụ | SW-DMZ, SW-SRV (2960-24TT); PORTAL, MAIL-GW, HIS-APP, PACS, AD-DNS, NMS, NVR (server); WLC |
| WAN | R-WAN1, R-WAN2 (2911) |
| Chi nhánh | R-DBP, R-BHTQ (2911); SW-DBP-1, SW-DBP-2, SW-BHTQ-1, SW-BHTQ-2 (2960-24TT) |
| Đầu cuối | Các PC và thiết bị đặt tên theo `generated/wiring.md`; thêm hai thiết bị không dây LAPTOP-STAFF và LAPTOP-GUEST kết nối vào AP-A |

Đặt tên thiết bị trong Packet Tracer đúng như bảng để trùng tên với `Configurations/`.

## 3. Đấu nối

Làm theo `generated/wiring.md` từng dòng. Packet Tracer tự nhận cáp nên có thể dùng "Automatically Choose Connection Type" cho các cổng đã ghi.

## 4. Nạp cấu hình theo thứ tự

1. ISP1, ISP2, INET.
2. FW-HCM (vào chế độ `enable`, rồi `configure terminal`, dán nội dung).
3. EDGE1, EDGE2.
4. CORE1, CORE2.
5. DS-A1, DS-A2, DS-B1, DS-B2.
6. ACC-A, ACC-B.
7. R-WAN1, R-WAN2 (làm bước giấy phép securityk9 trước).
8. R-DBP, R-BHTQ, rồi bốn switch chi nhánh.
9. Các switch SW-DMZ, SW-SRV chỉ cần cắm cáp, không cấu hình VLAN.

Mỗi file đã có `exit` đúng chỗ; dán từng khối nhỏ nếu Packet Tracer bị chậm khi dán cả file.

## 5. Cấu hình bằng giao diện

Địa chỉ tĩnh (gateway nằm trong `generated/links.md` và `generated/ip-plan.md`):

| Thiết bị | IP | Gateway |
|---|---|---|
| HIS-APP | 10.10.36.66/28 | 10.10.36.65 |
| PACS | 10.10.36.68/28 | 10.10.36.65 |
| AD-DNS | 10.10.36.70/28 | 10.10.36.65 |
| NMS | 10.10.36.72/28 | 10.10.36.65 |
| NVR | 10.10.36.73/28 | 10.10.36.65 |
| PORTAL | 10.10.36.82/28 | 10.10.36.81 |
| MAIL-GW | 10.10.36.83/28 | 10.10.36.81 |
| WEB-INET | 192.0.2.10/24 | 192.0.2.1 |
| TELE-PC | 198.51.101.10/24 | 198.51.101.1 |
| SRV-DBP | 10.20.5.98/29 | 10.20.5.97 |
| SRV-BHTQ | 10.30.5.98/29 | 10.30.5.97 |

Bật dịch vụ HTTP trên PORTAL và WEB-INET (Services > HTTP). Các PC khác để DHCP. WLC: địa chỉ quản trị 10.10.36.4/26, gateway 10.10.36.1; tạo hai WLAN (staff gắn VLAN 320, guest gắn VLAN 330) nếu Packet Tracer của bạn hỗ trợ; nếu không, dùng AccessPoint-PT độc lập và gắn cổng switch.

VPN người dùng từ xa (nếu có): trên TELE-PC mở Desktop > VPN, nhập group `HOSPITAL-VPN`, key `HospitalVPN2026`, máy chủ `203.0.113.2`, người dùng `teleuser`. Các mật khẩu trong thư mục `Configurations/` là giá trị dùng riêng cho bài lab.

## 6. Kiểm tra sau khi nạp

| Lệnh | Thiết bị | Kết quả mong đợi |
|---|---|---|
| `show standby brief` | DS-A1, DS-A2 | Mỗi VLAN một Active, một Standby, chia đều hai thiết bị |
| `show ip ospf neighbor` | CORE1 | Thấy DS-A1, DS-A2, DS-B1, DS-B2, R-WAN1 |
| `show ip route` | CORE2 | Có route mặc định E2 học từ OSPF |
| `show ip dhcp binding` | DS-A1, DS-A2 | Mỗi PC nhận địa chỉ từ một trong hai |
| `show crypto isakmp sa` | R-WAN1 | QM_IDLE sau khi ping qua WAN |
| `show ip nat translations` | EDGE1, EDGE2 | Thấy PAT và static NAT |

## 7. Kịch bản kiểm thử cho buổi demo

Mọi kết quả phải chụp màn hình và đưa vào báo cáo.

| STT | Kịch bản | Thao tác | Kết quả mong đợi |
|---|---|---|---|
| 1 | Cùng VLAN | PC-A-OUTPATIENT-1 ping PC-A-OUTPATIENT-2 | Thành công |
| 2a | Khác VLAN, cùng tòa | PC-A-RECEPTION ping PC-A-LAB | Thành công, traceroute qua 10.10.2.1 (VIP HSRP) |
| 2b | Khác VLAN, khác tòa | PC-A-OUTPATIENT-1 ping PC-B-INPATIENT-1 | Thành công qua core |
| 3a | Trụ sở và chi nhánh | PC-A-OUTPATIENT-1 ping PC-DBP-CLINIC-1 và PC-BHTQ-CLINIC-1 | Thành công; traceroute qua R-WAN |
| 3b | Hai chi nhánh | PC-DBP-CLINIC-1 ping PC-BHTQ-CLINIC-1 | Thành công qua trụ sở |
| 4a | Server trong DMZ từ LAN | PC-A-OUTPATIENT-1 mở http://10.10.36.82 | Mở được |
| 4b | Server trong DMZ từ Internet | WEB-INET (hoặc TELE-PC) mở http://203.0.113.3 | Mở được |
| 4c | DMZ không vào được LAN | Từ PORTAL ping 10.10.2.x | Không thành công |
| 5 | Thiết bị khách không vào LAN | Laptop khách (VLAN 330) ping PC-A-RECEPTION, PC-DBP-CLINIC-1, HIS-APP | Không thành công |
| 5b | Khách ra Internet | Laptop khách mở http://192.0.2.10 | Mở được |
| 6a | Web server Internet | PC-A-RECEPTION mở http://192.0.2.10 | Mở được |
| 6b | Traceroute ra Internet | tracert 192.0.2.10 | Qua VIP, core, firewall, EDGE, ISP, INET |
| 6c | Chia tải | Chạy lần lượt nhiều PC, xem `show ip nat translations` trên EDGE1 và EDGE2 | Cả hai có bản dịch |
| 7 | HSRP | Tắt cổng DS-A1 hướng lên core; ping liên tục từ PC | Mất tối đa vài gói rồi tự phục hồi qua DS-A2 |
| 8 | Chuyển đổi Internet | `shutdown` Gi0/1 trên EDGE1 | Ping ra 192.0.2.10 vẫn thông qua EDGE2 |
| 9 | VPN | TELE-PC kết nối VPN rồi mở HIS-APP | Mở được; không thông tới các mạng khác |
| 10 | Chặn theo ACL | Camera ping HIS-APP; thiết bị y tế ping PC | Không thành công; ping NVR/HIS thành công |

## 8. Kết quả kiểm chứng trong Packet Tracer 9.0.1

Mô phỏng đã dựng bằng script (78 thiết bị, 85 trong 86 liên kết, thiếu liên kết WLC vì không có mẫu WLC) và lưu tại `Simulation/hospital-network.pkt`. Các thiết bị đầu cuối gom thành 12 cụm theo từng switch để dễ nhìn.

### Tính năng đã kiểm chứng

| Tính năng | Kết quả |
|---|---|
| HSRP trên Catalyst 3650-24PS | Chạy; CORE1 là Active cho VLAN 320, 330, 399 và thấy Standby ở CORE2 |
| OSPF | CORE1 có 6 neighbor FULL (CORE2, DS-A1, DS-A2, DS-B1, DS-B2, R-WAN1); R-WAN1 học đủ route của trụ sở |
| IPsec trên 2911 | Cần cấp `securityk9` (license, `write memory`, `reload`); sau đó nạp cấu hình không lỗi |
| ASA 5506-X | Cấu hình được qua tab CLI của thiết bị (script không truy cập được CLI của ASA) |
| DHCP chia đôi dải trên DS-A1 và DS-A2 | PC nhận địa chỉ sau `ipconfig /renew`; chi nhánh cũng nhận địa chỉ |
| Ping và gateway | PC lấy đúng gateway là VIP HSRP |

### Kịch bản đã chạy

| Kịch bản | Kết quả |
|---|---|
| 1 Cùng VLAN | Thông |
| 2a Khác VLAN, cùng tòa | Thông, TTL 127 (qua một router) |
| 2b Khác VLAN, khác tòa | Thông (mất gói đầu do ARP) |
| 3a Trụ sở sang DBP và BHTQ | Thông, TTL 124 và 122 |
| 3b DBP sang BHTQ | Thông |
| 6a Ra Internet | PC trụ sở ping được WEB-INET 192.0.2.10 (TTL 122) |
| 10 ACL | Camera ping HIS-APP và thiết bị y tế ping PC: không thông; camera ping NVR: thông |
| 4c DMZ không vào LAN | PORTAL ping PC LAN: không thông |

### Điểm Packet Tracer khác với thiết bị thật

- ASA trong Packet Tracer không nhận từ khóa `https`, `ntp`, `log` và không có `time-exceeded`; cấu hình dùng cổng 443, 123, bỏ `log`. ACL không thể xóa cả nhóm bằng `clear configure access-list`, phải xóa từng dòng; thứ tự dòng quyết định kết quả nên dòng `deny` tới LAN đặt trước các dòng `permit`.
- ASA trong Packet Tracer không theo dõi trạng thái ICMP: ping từ LAN tới PORTAL không có hồi đáp vì `DMZ-IN` chặn gói trả về tới 10.0.0.0/8. Cách kiểm tra đúng là mở HTTP từ PC tới 10.10.36.82.
- Lệnh `crypto ipsec transform-set` không vào chế độ con, nên không có `exit` ngay sau đó.
- Easy VPN: lệnh `acl` trong nhóm `crypto isakmp client configuration group` không được nhận, nên không cấu hình split tunnel; ACL 120 vẫn được định nghĩa trên EDGE1.
- Lệnh `terminal length 0` không được nhận; script `tracert` chỉ trả về tiêu đề, cần chụp màn hình Command Prompt để lấy các hop.
- Reload nhiều router cùng lúc làm Packet Tracer đóng đột ngột; cấp license từng hai router một và lưu file trước mỗi lần.

### Còn lại

Kịch bản 4a, 4b, 5, 6b, 6c, 7, 8, 9 chưa chạy trong mô phỏng: cần mở trình duyệt web trên PC, LAPTOP-GUEST nối AP-A, tắt cổng để kiểm tra HSRP và chuyển đổi Internet, Easy VPN trên TELE-PC. WLC chưa dựng nên SSID hiện chỉ trình bày trong thiết kế.

## 9. Nộp bài

Lưu file `.pkt` vào thư mục `Simulation/`, báo cáo vào `Report/`; tải cả hai lên BKeL.
