# 06 - Đánh giá, vấn đề còn lại và hướng phát triển (Bước 6)

## 1. Đánh giá thiết kế

### Độ tin cậy

- Mọi thiết bị lõi đều có cặp dự phòng (edge, firewall, core, distribution, WLC) và mỗi switch access có hai uplink về hai distribution.
- HSRP và STP rapid-PVST được căn khớp để hai distribution cùng chia tải ở trạng thái bình thường và tiếp quản nhau khi một bên hỏng.
- Hai đường Internet qua hai nhà mạng; mất một đường thì đường còn lại gánh toàn bộ (đề xuất 1 Gbps mỗi đường, tải sau 5 năm là 600 Mbps).
- Đối chiếu TT 54/2017/TT-BYT: hoạt động 24/7, thời gian giữa hai sự cố lớn hơn 4 giờ, phục hồi 70% trong 1 giờ và toàn bộ trong 24 giờ. Thiết kế có dự phòng ở mọi điểm đơn, nhưng các con số thời gian phục hồi phải đo thực tế khi vận hành, không thể chứng minh bằng mô phỏng.

### Khả năng nâng cấp

- Dải địa chỉ mỗi khối còn trống; trụ sở dùng dưới 10% của khối /16 (xem `generated/ip-plan.md`).
- Distribution có thêm cổng 10G và 40G; core có cổng trống để thêm tòa nhà thứ ba.
- Mỗi subnet có 20% dự phòng; mỗi switch access dự phòng 20% cổng.
- Khi lưu lượng Internet vượt 1 Gbps chỉ cần nâng gói cước, không đổi thiết kế.

### Phần mềm và cấu hình

- Cấu hình thiết bị sinh từ một mô hình dữ liệu duy nhất (`tools/model.py`, `tools/topology.py`) và được kiểm tra tự động: không trùng VLAN, không trùng subnet, đủ chỗ cho số host, tổng máy trạm khớp 600 và 260. Thay đổi địa chỉ chỉ cần sửa một chỗ rồi chạy lại.
- Nên đồng bộ phiên bản hệ điều hành thiết bị, sao lưu cấu hình hằng ngày vào NMS, đặt syslog tập trung.

### An toàn vật lý và điện

- Phòng máy: UPS tối thiểu 30 phút, điều hòa dự phòng, cảm biến nhiệt độ, độ ẩm, khói, hệ thống chữa cháy khí sạch, kiểm soát ra vào bằng thẻ và ghi log.
- Tủ IDF khóa, giám sát bằng camera; cáp quang đi trong ống riêng, tránh chung ống với cáp điện công suất.
- Thiết bị y tế cách ly mạng khỏi khách và khỏi máy trạm hành chính để hạn chế rủi ro cho bệnh nhân khi có sự cố mạng.

### Bảo mật

Xem mục 2 cho các lớp bảo vệ. Điểm mạnh là phân vùng nhiều lớp (VLAN, ACL tại gateway, firewall vùng, VPN có kiểm soát). Điểm cần theo dõi là IPS/IDS và phát hiện phishing chỉ có trong thiết kế.

## 2. Phần mở rộng cho kỹ sư tài năng: bảo mật

### Tường lửa

Firewall vùng (`Configurations/FW-HCM.txt`):

- Bốn mức tin cậy: outside 0, dmz 50, servers 90, inside 100.
- Outside chỉ nhận ICMP trả lời, cổng 80 và 443 tới portal, cổng 25 tới mail gateway, và HTTPS từ VPN pool tới HIS; còn lại bị chặn và ghi log.
- DMZ không được khởi tạo kết nối vào mạng nội bộ; ngoại lệ duy nhất là portal gọi API HIS cổng 8443.
- Server farm chỉ được ra Internet bằng HTTP/HTTPS/NTP; NMS được giám sát thiết bị qua SNMP/ICMP.

### ACL

- `ACL-GUEST` tại SVI VLAN 330 (core) và tại router chi nhánh: cho DHCP, DNS tới server DNS, chặn 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, cho phần còn lại ra Internet.
- `ACL-CCTV` tại VLAN camera: chỉ cho phép tới NVR.
- `ACL-MEDDEV` tại VLAN thiết bị y tế: chỉ cho phép tới HIS, PACS, LIS (và server cục bộ ở chi nhánh).
- Mọi ACL cho DHCP và hello HSRP để không làm hỏng dịch vụ nền.
- NAT edge có điều kiện loại trừ VPN pool để lưu lượng VPN không bị dịch địa chỉ.

### IDS/IPS (chỉ thiết kế)

- Đặt inline ngay sau firewall (hoặc module trên NGFW) để thấy lưu lượng outside và DMZ; thêm một cảm biến IDS thụ động nhận SPAN từ core để thấy lưu lượng đông-tây.
- Chế độ học 2 tuần ở chế độ chỉ phát hiện, sau đó bật chặn cho các chữ ký mức nghiêm trọng cao; tránh chặn nhầm thiết bị y tế dùng giao thức riêng.
- Gửi sự kiện về NMS/SIEM; kiểm tra chữ ký hằng tuần.

### Hướng dẫn thực hành bảo mật (best practice)

1. Quản trị thiết bị: SSH phiên bản 2, tắt Telnet, tài khoản riêng cho từng quản trị viên (AAA qua TACACS+/RADIUS), giới hạn nguồn quản trị về VLAN quản trị.
2. Mật khẩu: thay toàn bộ mật khẩu lab trong `Configurations/` trước khi triển khai thật; lưu bằng trình quản lý bí mật.
3. Cổng không dùng: tắt cổng, đặt vào VLAN trống; bật port-security, DHCP snooping, dynamic ARP inspection và BPDU guard trên switch access.
4. Cập nhật firmware có kế hoạch, thử trên thiết bị thử nghiệm trước.
5. Phân tách: bám theo ma trận vùng của tài liệu 02; không mở rule `any any`.
6. Nhật ký: syslog tập trung, đồng bộ NTP, lưu tối thiểu 12 tháng.
7. WiFi: 802.1X cho nhân viên, captive portal và client isolation cho khách.
8. Sao lưu: sao lưu hằng ngày, một bản ngoại tuyến, thử khôi phục định kỳ.
9. VPN: xác thực đa yếu tố cho người làm việc từ xa, chỉ mở HIS, thu hồi tài khoản khi nghỉ việc.
10. Diễn tập: ít nhất mỗi năm một lần kiểm thử xâm nhập và diễn tập mất điện/mất đường truyền.

## 3. Vấn đề còn lại

- Chưa kiểm chứng trong Packet Tracer: HSRP trên 3650, ECMP trên ASA, Easy VPN, WLC với LAP (xem bảng tại tài liệu 05).
- IPS/IDS, lọc URL, phát hiện phishing, GPON không mô phỏng được.
- Chi phí thiết bị và thuê bao chưa có báo giá thật.
- Chuyển đổi dự phòng khi nhà mạng hỏng ngầm (link vẫn lên nhưng không ra Internet) cần IP SLA hoặc giám sát đường đi; cấu hình hiện chỉ xử lý được mất link.
- Lưu lượng bất đối xứng với dịch vụ công bố qua hai nhà mạng cần kiểm tra thêm: chỉ nên công bố dịch vụ ra ngoài trên một địa chỉ và dùng DNS cho dự phòng.
- Số AP và số cổng là ước tính, phải xác minh bằng khảo sát thực tế.

## 4. Hướng phát triển

- BGP với dải địa chỉ độc lập để có chuyển đổi dự phòng Internet đúng nghĩa và công bố dịch vụ qua cả hai nhà mạng.
- SD-WAN cho chi nhánh để dùng thêm đường băng rộng giá rẻ làm dự phòng có chọn đường theo ứng dụng.
- Phân đoạn vi mô (NAC, dán nhãn thiết bị theo hồ sơ) cho thiết bị y tế.
- Mạng WiFi riêng cho thiết bị y tế không dây, định vị tài sản bằng AP.
- SIEM và SOC giám sát 24/7; tự động hóa cấu hình và kiểm tra tuân thủ.
