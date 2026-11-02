# 05 - Dựng mô phỏng và kiểm thử (Bước 4 và 5)

Phiên bản đã cài: Packet Tracer 8.2.2 và 9.0.1. Cấu hình của mọi thiết bị nằm trong thư mục `Configurations/`, sinh từ `tools/design.py`. Thư mục này chứa lệnh IOS/ASA thuần, dán vào CLI từng thiết bị theo thứ tự dưới đây.

## 1. Tính năng rủi ro trong Packet Tracer và kết quả thử

Những điểm này đã được thử trực tiếp trên Packet Tracer 9.0.1; cột cuối ghi kết quả, chi tiết ở mục 8.

| Tính năng | Rủi ro | Phương án thay thế | Kết quả thử |
|---|---|---|---|
| HSRP (`standby`) trên Catalyst 3650-24PS | Có thể không hỗ trợ | Đổi sang 3560-24PS, thêm `switchport trunk encapsulation dot1q` trước `switchport mode trunk` | Chạy được, không cần đổi switch |
| ASA 5506-X: hai route mặc định bằng nhau qua hai giao diện (ECMP) | Có thể chỉ dùng một route | Giữ một route mặc định qua EDGE1; chia tải chứng minh bằng cách ép lưu lượng từ nửa số VLAN qua EDGE2 trên core | ECMP làm NAT và đường về lệch; thay bằng hai tuyến /1 chia theo đích, mỗi tuyến có tuyến dự phòng ở ISP còn lại (kịch bản 6c) |
| IPsec trên Cisco 2911 | Cần gói security | Nhập `license boot module c2900 technology-package securityk9`, xác nhận `yes`, `write memory`, `reload` | Đã cấp license cho 4 router, cấu hình nạp được |
| Easy VPN và VPN client trên PC | Có thể không có | Chỉ trình bày trong báo cáo và dùng site-to-site IPsec làm bằng chứng | VPN client có sẵn trên PC, kết nối thành công (kịch bản 9) |
| WLC và LAP | Cách LAP tìm WLC có thể khác | Dùng AP độc lập (AccessPoint-PT) với hai SSID, VLAN gắn trên cổng switch | Không có mẫu WLC; dùng AccessPoint-PT làm AP khách gắn VLAN 330 qua cổng access của CORE1, kịch bản 5 và 5b chạy được |
| Chuyển đổi dự phòng tự động khi nhà mạng hỏng | Cần IP SLA/track | Mô phỏng bằng cách `shutdown` cổng EDGE1 Gi0/1 | Chạy được qua tuyến dự phòng của ASA (kịch bản 8) |
| IPS/IDS, lọc URL, phát hiện phishing | Packet Tracer không mô phỏng | Chỉ trình bày trong thiết kế và báo cáo | Không mô phỏng |
| GPON | Không có OLT/ONT như đề | Chỉ trình bày trong thiết kế | Không mô phỏng |

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
| 5 | Thiết bị khách không vào LAN | Thiết bị khách (smartphone, VLAN 330) ping PC-A-RECEPTION, PC-DBP-CLINIC-1, HIS-APP | Không thành công |
| 5b | Khách ra Internet | Thiết bị khách mở http://192.0.2.10 | Mở được |
| 6a | Web server Internet | PC-A-RECEPTION mở http://192.0.2.10 | Mở được |
| 6b | Traceroute ra Internet | tracert 192.0.2.10 | Qua VIP, core, firewall, EDGE, ISP, INET |
| 6c | Chia tải | Ping 8.8.8.8 và 192.0.2.10 từ HIS-APP, xem `show ip nat translations` trên EDGE1 và EDGE2 | Cả hai có bản dịch |
| 7 | HSRP | Tắt cổng DS-A1 hướng lên core; ping liên tục từ PC | Mất tối đa vài gói rồi tự phục hồi qua DS-A2 |
| 8 | Chuyển đổi Internet | `shutdown` Gi0/1 trên EDGE1 | Ping ra 192.0.2.10 vẫn thông qua EDGE2 |
| 9 | VPN | TELE-PC kết nối VPN rồi mở HIS-APP | Mở được; không thông tới các mạng khác |
| 10 | Chặn theo ACL | Camera ping HIS-APP; thiết bị y tế ping PC | Không thành công; ping NVR/HIS thành công |

## 8. Kết quả kiểm chứng trong Packet Tracer 9.0.1

Mô phỏng đã dựng bằng script (78 thiết bị, 85 trong 86 liên kết, WLC là AccessPoint-PT) và lưu tại `Simulation/hospital-network.pkt`. Các thiết bị đầu cuối gom thành 12 cụm theo từng switch để dễ nhìn.

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
| 3a Trụ sở sang DBP và BHTQ | PC-A-PHARMACY ping 10.20.0.11 và 10.30.0.11 đều 4/4, TTL 124; `tracert 10.20.0.11` đi qua 10.10.3.131, 172.16.2.2, 172.16.1.2, 172.16.1.10 rồi tới máy đích sau 5 hop |
| 2c Khác tòa | PC-B-TRAINING 10.10.20.11 ping PC-A-PHARMACY 10.10.3.139 đạt 4/4, TTL 125 |
| 3b DBP sang BHTQ | Thông |
| 6a Ra Internet | PC trụ sở ping được WEB-INET 192.0.2.10 (TTL 122) |
| 10 ACL | Camera ping HIS-APP và thiết bị y tế ping PC: không thông; camera ping NVR: thông |
| 3c IPsec site-to-site | Ping từ HIS-APP tới SRV-DBP kích hoạt IKE; `show crypto isakmp sa` trên R-WAN1 có cặp 172.16.1.10 và 172.16.1.9 ở trạng thái QM_IDLE, ACTIVE (vài gói đầu mất trong lúc thương lượng) |
| 5 Thiết bị khách không vào LAN | GUEST-PHONE (smartphone) nối SSID HOSPITAL-GUEST, nhận địa chỉ trong 10.10.34.0/23 (lần kiểm gần nhất là 10.10.34.12) với gateway 10.10.34.1; ping HIS-APP 10.10.36.66 và PC 10.10.20.11 đều nhận `Destination host unreachable` từ 10.10.34.2 trên CORE1, mất 100% gói |
| 5b Khách ra Internet | GUEST-PHONE mở http://192.0.2.10 thấy trang chủ của WEB-INET; ping 192.0.2.10 TTL 123 |
| 4a, 4b HTTP | PC-A-PHARMACY mở được http://10.10.36.82 (PORTAL); TELE-PC mở được PORTAL qua địa chỉ NAT tĩnh 203.0.113.3 |
| 4c DMZ không vào LAN | PORTAL ping PC LAN: không thông |
| 6a, 6b Web và traceroute ra Internet | PC-A-PHARMACY mở được http://192.0.2.10. Từ PC-B-TRAINING, `tracert 8.8.8.8` qua 10.10.20.2, 172.16.3.2, 172.16.0.9, 172.16.0.2 (EDGE1), 203.0.113.1 (ISP1) rồi tới 8.8.8.8 sau 6 hop; `tracert 192.0.2.10` qua 10.10.20.2, 172.16.3.10, 172.16.0.9, 172.16.0.6 (EDGE2), 198.51.100.1 (ISP2), 100.64.2.2 rồi tới WEB-INET sau 7 hop. PC-B-TRAINING ping 8.8.8.8 đạt 4/4, TTL 250 |
| 6c Chia tải hai đường Internet | ASA chia không gian địa chỉ Internet làm hai nửa: 0.0.0.0/1 ưu tiên outside1 (EDGE1), 128.0.0.0/1 ưu tiên outside2 (EDGE2), mỗi nửa là đường dự phòng của nửa kia. Ping từ HIS-APP tới 8.8.8.8 (nửa đầu, loopback trên INET) có bản dịch PAT 203.0.113.2 trên EDGE1; ping tới 192.0.2.10 (nửa sau) có bản dịch PAT 198.51.100.2 trên EDGE2. Khi tắt Gi0/1 của EDGE1, ping 8.8.8.8 vẫn thông 5/6 qua EDGE2 |
| 6d NAT tĩnh | `show ip nat translations` trên EDGE1 có 3 bản dịch tĩnh (PORTAL 80 và 443, MAIL-GW 25) |
| 7 HSRP | Tắt bốn cổng của DS-A1: ping WEB-INET 4/4, ping PC-DBP 2/4 trong lúc OSPF hội tụ; DS-A2 nhận vai trò Active; bật lại cổng thì DS-A1 giành lại Active nhờ preempt |
| 8 Chuyển đổi Internet | `shutdown` Gi0/1 EDGE1: ping WEB-INET mất 1 gói rồi thông 3/4 qua EDGE2 (TTL 122) |
| 9 Easy VPN | TELE-PC nhập nhóm HOSPITAL-VPN, máy chủ 203.0.113.2, báo VPN is connected và nhận 192.168.99.10; ping HIS-APP 10.10.36.66 đạt 3/4 (TTL 126, mất gói đầu do ARP); ping PC 10.10.20.11 không thông |

### Điểm Packet Tracer khác với thiết bị thật

- ASA trong Packet Tracer không nhận từ khóa `https`, `ntp`, `log` và không có từ khóa `time-exceeded`; cấu hình dùng cổng 443, 123, bỏ `log`. ACL không thể xóa cả nhóm bằng `clear configure access-list`, phải xóa từng dòng; thứ tự dòng quyết định kết quả nên dòng `deny` tới LAN đặt trước các dòng `permit`.
- ASA trong Packet Tracer không theo dõi trạng thái ICMP: ping từ LAN tới PORTAL không có hồi đáp vì `DMZ-IN` chặn gói trả về tới 10.0.0.0/8. Cách kiểm tra đúng là mở HTTP từ PC tới 10.10.36.82.
- Lệnh `crypto ipsec transform-set` không vào chế độ con, nên không có `exit` ngay sau đó.
- Easy VPN: lệnh `acl` trong nhóm `crypto isakmp client configuration group` không được nhận, nên không cấu hình split tunnel; ACL 120 vẫn được định nghĩa trên EDGE1.
- Lệnh `terminal length 0` không được nhận; script `tracert` chỉ trả về tiêu đề, cần chụp màn hình Command Prompt để lấy các hop.
- Tuyến mặc định của ASA: hai tuyến cùng đích làm ECMP khiến NAT và đường về lệch nhau, nên chia theo đích bằng 0.0.0.0/1 và 128.0.0.0/1 (mỗi nửa một ISP chính, metric 1, và một tuyến dự phòng, metric 2, qua ISP còn lại), kèm tuyến máy chủ tới 172.16.0.2, 172.16.0.6 và 172.16.0.10. Packet Tracer còn sinh thêm hai tuyến connected sai (172.16.0.0/30 trên outside2 và inside) nên cần các tuyến máy chủ này để định tuyến đúng.
- ACL trên ASA không theo dõi TCP: gói trả về từ DMZ phải được cho phép rõ ràng, dòng `permit tcp 10.10.36.80 255.255.255.240 any` đặt trước dòng `deny` tới 10.0.0.0/8.
- Để lưu lượng TCP trả về từ Internet vào được mạng nội bộ (HTTP từ khách và PC ra Internet), OUT-IN thêm dòng `permit tcp any 10.0.0.0 255.0.0.0`, đặt sau dòng `deny` nguồn từ dải VPN (192.168.99.0/24) và trước `deny ip any any`. ASA thật theo dõi trạng thái nên không cần dòng này.
- ACL của ASA trong Packet Tracer chỉ nhận ba loại ICMP là echo, echo-reply và unreachable, không lọc được time-exceeded. Để traceroute từ LAN ra Internet hiện đủ hop, OUT-IN cho phép ICMP có nguồn từ các dải liên kết của nhà mạng là 172.16.0.0/16, 203.0.113.0/29, 198.51.100.0/29 và 100.64.0.0/10. Ping từ Internet vào LAN vẫn bị chặn.
- ARP trên ASA trong Packet Tracer không gắn với từng cổng. Khi cổng outside1 chớp tắt, tuyến nửa dưới tạm chuyển sang outside2 và ASA ghi địa chỉ MAC học được qua outside2 cho đích như 8.8.8.8. Khi outside1 hoạt động lại, ASA gửi gói ra EDGE1 nhưng vẫn dùng MAC cũ nên EDGE1 loại gói, ping ra Internet mất 100% trong khi mọi thứ khác vẫn thông. Packet Tracer không có `clear arp` hay `arp timeout`; cách xử lý là chạy `shutdown` rồi `no shutdown` trên cổng giữ các mục ARP sai, ở đây là Gi1/2, lúc không có lưu lượng. Lỗi này nhìn thấy rõ nhất trong chế độ Simulation, nơi EDGE1 báo địa chỉ MAC đích không khớp với cổng nhận. ASA thật lưu ARP riêng cho từng cổng nên không bị.
- Sau reload, các cổng ASA ở trạng thái `shutdown`, phải `no shutdown` và `write memory` lại.
- Sau `ipconfig /renew`, TELE-PC mất địa chỉ tĩnh vì còn cờ DHCP; script đặt `setDhcpClientFlag(false)` trước khi gán địa chỉ.
- Sau khi mở lại file `.pkt`, mạng cần khoảng một phút hội tụ; thao tác VPN ngay lúc đó sẽ báo `Connection timed out`, thử lại sau khi ping tới 203.0.113.2 thông là kết nối được.
- Reload nhiều router cùng lúc làm Packet Tracer đóng đột ngột; cấp license từng hai router một và lưu file trước mỗi lần.

### Phần chưa mô phỏng được

WLC thật không có trong Packet Tracer. Thiết bị WLC trong mô phỏng là một AccessPoint-PT phát SSID HOSPITAL-GUEST (WPA2-PSK) nối vào cổng Gi1/0/8 của CORE1 đặt ở VLAN 330; SSID nhân viên không được dựng vì AccessPoint-PT chỉ gắn một VLAN theo cổng switch. Cách cách ly khách vẫn được kiểm chứng đầy đủ nhờ SVI VLAN 330 và ACL-GUEST trên CORE1.

## 9. Nộp bài

Lưu file `.pkt` vào thư mục `Simulation/`, báo cáo vào `Report/`; tải cả hai lên BKeL.
