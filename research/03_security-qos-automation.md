# Nghiên cứu 03 - Security, QoS, Automation (Step 7, 8, 9)

## 1. Layer 2 security (Step 7)

Thứ tự bắt buộc: bật DHCP Snooping trước, vì nó tạo bảng binding mà DAI và IP Source Guard dựa vào.

DHCP Snooping:
- Chặn DHCP server giả. Port hướng tới DHCP server hợp lệ hoặc uplink là trusted; DHCP reply trên port untrusted bị loại và có thể bị shutdown.
- Lệnh chính: ip dhcp snooping, ip dhcp snooping vlan, ip dhcp snooping trust, ip dhcp snooping limit rate.
- Kiểm tra: show ip dhcp snooping, show ip dhcp snooping binding.
- Lưu ý thiết kế TVI: DHCP server ở HQ và relay ở chi nhánh; port trunk giữa switch phải đặt trust, và cần chú ý option 82 khi dùng relay.

Dynamic ARP Inspection:
- Chống ARP poisoning bằng cách đối chiếu ARP với binding của DHCP snooping hoặc ARP ACL tĩnh (cho host cấp IP tĩnh như server).
- Link giữa switch đặt trust. Lệnh: ip arp inspection vlan, ip arp inspection trust, ip arp inspection validate.
- Kiểm tra: show ip arp inspection.

Port Security (tùy chọn thêm): giới hạn số MAC mỗi port, kết hợp IP Source Guard để chống giả MAC/IP.

Cần test trên image lab: tôi chưa tìm được tài liệu xác nhận IOL-L2/IOSvL2 hỗ trợ DAI hay không.

## 2. ACL, NAT, hardening

Những điều đề yêu cầu: ACL cô lập Guest khỏi Corp, tách IoT, NAT overload ra internet, tắt Telnet/HTTP/SNMPv1-v2c để dùng SSHv2/HTTPS/SNMPv3.

Nguyên tắc cần nắm (kiến thức chung, chưa tra nguồn riêng):
- Extended ACL đặt gần nguồn; rule được xét theo thứ tự, có deny ngầm cuối.
- Guest: chỉ cho ra internet, chặn tới dải RFC1918 nội bộ. IoT: chỉ cho tới server/gateway cần thiết.
- NAT overload (PAT) trên edge router với inside/outside đúng interface.
- Micro-segmentation, zone-based firewall, ZTNA/SASE: trình bày ở mức thiết kế trong báo cáo, vì lab Cisco ảo khó mô phỏng trọn vẹn.

Cần nghiên cứu thêm khi tới Step 7: cú pháp ACL IPv6, và kiểm chứng bằng ping/telnet bị chặn có log đếm hit (show access-lists).

## 3. QoS (Step 8)

Mẫu MQC từ Cisco community:
- class-map match DSCP EF cho voice; class signaling riêng.
- policy-map con dùng LLQ (priority percent) cho voice, bandwidth percent cho signaling, class-default fair-queue.
- policy-map cha shape toàn link về tốc độ WAN rồi gọi policy con; áp service-policy output lên interface WAN.
- Phần trăm tính trên tốc độ đã shape.
- Kiểm tra: show policy-map interface <if>.

Khác biệt với đề: bài mẫu dùng CS3 cho signaling và không có AF31. Đề yêu cầu EF cho voice và AF31 cho video, nên cần thêm một class AF31 (ví dụ bandwidth percent) và giải thích lý do trong báo cáo.

Rủi ro đã ghi nhận: tài liệu CML nói QoS trên IOSv chưa được kiểm thử và chưa hỗ trợ chính thức ("may work"). Cần thử sớm. Kỹ thuật chứng minh: tạo traffic có DSCP bằng ping với ToS hoặc IP SLA, rồi đọc counter của class trong show policy-map interface.

Marking ở biên: nên mark/trust ở access switch hoặc edge, nêu trong báo cáo vì sao.

## 4. Automation (Step 9)

Python + Netmiko:
- Tham số kết nối đặt trong dict rồi ConnectHandler(**params); device_type cisco_ios; có enable().
- send_command cho show; send_config_set cho danh sách lệnh cấu hình; send_config_from_file đọc lệnh từ file. Nên dùng with ConnectHandler(...) để đóng phiên sạch.
- Bắt NetmikoTimeoutException và NetmikoAuthenticationException (đề yêu cầu), thêm except cho lỗi khác để một node chết không làm script dừng.
- send_command có max_loops mặc định 500 và có thể ném exception nếu lệnh không xong.
- Credentials: getpass hoặc biến môi trường, không để trong file.
- Idempotency (30% điểm Step 9): so sánh trạng thái hiện tại (ví dụ show vlan brief) với trạng thái mong muốn trước khi gửi lệnh, chỉ gửi phần thiếu. Đây là phần đề starter code còn thiếu: mẫu starter luôn gửi toàn bộ lệnh mỗi lần.
- Logging: logging ra logs/automation.log; backup có timestamp vào backups/ theo dạng hostname_timestamp_backup.cfg.
- Trước và sau thay đổi đều phải chụp show running-config và show ip interface brief.

Ansible:
- Dùng module cisco.ios.ios_vlans (network resource module) với state merged: chỉ thay đổi phần khác với thiết bị, nên idempotent. Các state khác: replaced, overridden, deleted, gathered (đọc không đổi).
- ios_command để lấy running-config, ios_config cho NTP/banner.
- Credentials bằng Ansible Vault (nguồn tôi đọc không bàn về Vault; cần đọc tài liệu Ansible chính thức khi làm).
- Lưu ý: ios_config với dòng banner có thể báo changed mỗi lần chạy, kiểm tra idempotency thực tế.

Chọn Python hay Ansible: Python cho phép kiểm soát và giải thích từng dòng (hợp phần oral defense), dễ thêm kiểm tra idempotency và logging theo đúng yêu cầu của đề. Ansible ít code hơn nhưng nhiều thứ ẩn trong module. Gợi ý: Python Netmiko.

Việc phải tránh: dán nguyên starter code (đề có chống đạo văn và yêu cầu giải thích 100%).
