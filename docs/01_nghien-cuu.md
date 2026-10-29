# 01 - Nghiên cứu

Tổng hợp từ các nguồn đã đọc để làm cơ sở thiết kế. Phần nào chưa kiểm chứng được ghi rõ là giả định.

## 1. Thiết kế mạng bệnh viện

- Mạng bệnh viện cần phân tách lưu lượng lâm sàng, thiết bị y tế và khách vào các VLAN riêng; VLAN kết thúc tại tường lửa thế hệ mới và việc định tuyến giữa các VLAN bị chặn hoặc kiểm soát chặt. Nguồn khuyến nghị: lưu lượng lâm sàng và khách không bao giờ dùng chung một broadcast domain.
- Thiết bị y tế (bơm tiêm, monitor) nên ở VLAN riêng, tách cả khỏi máy trạm lâm sàng lẫn khách, để giới hạn phạm vi lây lan khi một thiết bị bị tấn công.
- WiFi dùng hai SSID tách VLAN: SSID nội bộ xác thực 802.1X qua RADIUS, SSID khách có captive portal. Bật client isolation cho SSID khách, giới hạn tốc độ mỗi khách (ví dụ 8 Mbps xuống, 2 Mbps lên), dùng DSCP để ưu tiên lưu lượng quan trọng. Công suất tham khảo khoảng 25 Mbps mỗi giường bệnh.
- Trước khi vận hành phải kiểm thử: từ thiết bị khách thử truy cập địa chỉ mạng lâm sàng, mọi kết nối thành công là kiểm thử thất bại.
- Nguồn: Purple, hướng dẫn WiFi khách bệnh viện và tách mạng (https://www.purple.ai/en-us/guides/hospital-guest-wifi-patient-experience-and-network-separation).

## 2. Mô hình phân tầng và tỷ lệ oversubscription

- Mạng campus ba tầng (access, distribution, core). Tỷ lệ oversubscription tham khảo: access 20:1 (tổng băng thông cổng người dùng so với uplink), distribution lên core 4:1. Tỷ lệ phụ thuộc ứng dụng và cần đo thực tế.
- Nguồn: Noction, oversubscription in networking (https://www.noction.com/blog/oversubscription-in-networking).

## 3. Cáp có cấu trúc

- Sáu hệ thống con theo TIA-568: entrance facility, equipment room, backbone, telecom room, horizontal, work area. Cáp ngang tối đa 90 m độc lập với loại cáp; kênh truyền tối đa 100 m gồm cả dây nhảy.
- Cat6 chỉ đạt 10GBASE-T tối đa khoảng 55 m; Cat6A đạt 100 m cho cả 1G và 10G.
- Mỗi vùng làm việc nên có ít nhất hai ổ cắm.
- Nguồn: CablingInstall (https://cablinginstall.com/standards/article/16472159/know-the-6-subsystems-of-a-structured-cabling-system), Windy City Wire (https://windycitywire.com/blogs/UNDERSTANDING-DISTANCE-LIMITS-ACROSS-CAT5E-CAT6-AND-CAT6A-NETWORKS).

## 4. Lưu lượng hình ảnh y khoa (PACS)

- Kích thước ca chụp tham khảo từ ví dụ trong nguồn: CT 350 MB đến 1,2 GB, MRI 250 đến 400 MB, X-quang 20 đến 30 MB. Nên đo số liệu thật của bệnh viện và lấy trung vị.
- 1 Gbps đủ cho khoa nhỏ có CT/MRI vừa phải; 10 Gbps khi nhiều trạm đọc, truy xuất lưu trữ và xử lý 3D. Thiết kế theo giờ cao điểm, không theo trung bình; tách VLAN riêng và ưu tiên QoS cho DICOM; WAN thường là nút thắt nên cần bộ nhớ đệm cục bộ và lịch chuyển dữ liệu lớn vào ban đêm.
- Nguồn: GSE, PACS server capacity (https://gse.kz/en/blog/pacs-server-capacity-iops-network-dicom).

## 5. Lựa chọn kết nối WAN

- MPLS: chi phí cao nhất, chất lượng dự đoán được, QoS và SLA tích hợp, bảo mật tập trung; hạn chế là giá thuê mạch cao và khó mở rộng cho đám mây.
- SD-WAN: chi phí thấp hơn do chạy trên băng thông rộng thông thường, triển khai không cần can thiệp (zero-touch), chọn đường theo chỉ số thời gian thực; hạn chế là lo ngại bảo mật trên Internet, chất lượng ứng dụng trên băng thông rộng và độ phức tạp vận hành.
- Kênh thuê riêng (leased line): điểm nối điểm, băng thông không chia sẻ, đối xứng, riêng tư; nhà mạng cam kết hỗ trợ 24/7, phản hồi lỗi trong 30 phút và xử lý trong 120 phút theo nguồn tiếng Việt. Khác FTTH: băng thông FTTH chia sẻ và không đảm bảo.
- Nguồn: TelecomTrainer (https://www.telecomtrainer.com/mpls-vs-sd-wan-a-clear-comparison-for-modern-enterprise-networks/), BKNS (https://www.bkns.vn/?p=48949).
- Giá: các bảng giá cước đọc được (chogia.vn) có ngày đăng không rõ ràng, nên chỉ dùng làm ước lượng. Gói doanh nghiệp tham khảo: 500 Mbps khoảng 1,5 đến 2 triệu đồng mỗi tháng, 1 Gbps khoảng 2,5 đến 3 triệu đồng mỗi tháng. Không tìm được giá công khai của kênh thuê riêng hay MPLS tại Việt Nam, nên chi phí WAN trong thiết kế là giả định cần báo giá nhà mạng.

## 6. Hai đường Internet và chia tải

- Dự phòng đường Internet nên kích hoạt khi mất khả năng đi tới thượng nguồn, không chỉ khi giao diện down. Cách làm phổ biến: IP SLA ping địa chỉ ngoài kết hợp track và static route floating; các lỗi thường gặp là thăm dò đi nhầm đường và không tự quay lại đường chính. Giải pháp: gắn static route host riêng cho từng đích thăm dò, hoặc dùng EEM.
- Nguồn: Cisco Community (https://community.cisco.com/t5/routing/dual-isp-failover-ip-sla-route-maps-and-static-routes-problems/m-p/4282899).
- Giới hạn của đề: đề ghi DSL. ADSL/VDSL thông thường chỉ đạt vài chục Mbps đến khoảng 100 Mbps, trong khi ước tính sơ bộ cho thấy nhu cầu khoảng 0,5 đến 0,8 Gbps, nên cần hai đường cáp quang. Đây là kiến thức chung, không rút ra từ một nguồn cụ thể.

## 7. Camera giám sát

- Công thức: băng thông (Mbps) bằng tổng bitrate luồng chính nhân số camera cộng bitrate luồng phụ nhân số camera dùng luồng phụ.
- Bitrate tham khảo cho H.264: 1 MP khoảng 2 Mbps, 2 MP khoảng 4 Mbps, 4 MP khoảng 8 Mbps. Nguồn không có số H.265; giả định H.265 giảm khoảng một nửa so với H.264 (giả định, cần kiểm chứng theo model camera).
- Nguồn: Zositech (https://blog.zositech.com/ip-camera-bandwidth-calculation/).

## 8. Quy định tại Việt Nam

- Thông tư 54/2017/TT-BYT (Bộ tiêu chí ứng dụng CNTT tại cơ sở khám chữa bệnh) có các nhóm tiêu chí về mạng LAN và LAN không dây, đường truyền Internet, tường lửa, giám sát mạng, phòng máy chủ (phòng cháy chữa cháy, theo dõi nhiệt độ và độ ẩm, kiểm soát ra vào), camera an ninh. Bảo mật: kiểm soát truy cập, ghi vết, chống mã độc, tường lửa phân tách vùng Internet, máy chủ ứng dụng và mạng nội bộ, chống DoS/DDoS, sao lưu hàng ngày, mã hóa dữ liệu nhạy cảm. Độ tin cậy: hoạt động 24/7, thời gian giữa hai sự cố lớn hơn 4 giờ, phục hồi 70 phần trăm trong 1 giờ và 100 phần trăm trong 24 giờ.
- Một số tiêu chí về bệnh án điện tử có thể đã hết hiệu lực theo Thông tư 13/2025/TT-BYT; cần kiểm tra văn bản hiện hành trước khi trích trong báo cáo.
- Nguồn: Luatvietnam, Thông tư 54/2017/TT-BYT (https://luatvietnam.vn/y-te/thong-tu-54-2017-tt-byt-bo-y-te-158564-d1.html).

## 9. Packet Tracer

- ASA 5506-X được mô phỏng (phần mềm 9.6(1), giấy phép Security Plus): tối đa 8 cổng, 30 VLAN, hỗ trợ failover Active/Standby theo bảng giấy phép; tính năng FirePOWER (IPS, lọc nội dung) không được mô phỏng. Bài lab DMZ trên ASA dùng nameif, NAT đối tượng và ACL ngoài.
- VPN site-to-site IPsec trên router (crypto isakmp, transform-set, crypto map) có bài lab chính thức, cần bật gói security trên 2900. Chưa xác nhận được VPN truy cập từ xa (Easy VPN, PC client) trong Packet Tracer; cần thử trực tiếp.
- Packet Tracer 9 bổ sung thiết bị công nghiệp (IE-3400, ISA-3000) nhưng không có tính năng IDS/IPS cho mạng doanh nghiệp.
- Nguồn: packettracernetwork.com (https://www.packettracernetwork.com/features/cisco-packet-tracer-firewalls.html, https://www.packettracernetwork.com/labs/lab18-asa-dmz.html, https://packettracernetwork.com/features/packet-tracer-9-new-features.html), bài lab VPN Packet Tracer của Cisco NetAcad (https://ccna.ilkom.unsri.ac.id/4/course/files/7.1.2.4%20Packet%20Tracer%20-%20Configuring%20VPNs%20(Optional)%20Instructions.pdf).
- Máy trong nhóm đã cài Packet Tracer 8.2.2 và 9.0.1, nên các tính năng chưa xác nhận (HSRP trên switch L3, ASA ECMP, WLC, Easy VPN) sẽ được kiểm tra trực tiếp.

## 10. File Reference của đề

- Hướng dẫn NAT cho mạng hai site trên Packet Tracer: router biên LTK và DiAn thực hiện PAT cho mạng nội bộ ra địa chỉ công cộng duy nhất của cổng, static NAT theo cổng để truy cập web server nội bộ từ ngoài (172.28.16.1:1111 và 172.28.18.2:2222), router ISP ở giữa chỉ chạy OSPF. Thiết kế của nhóm dùng cùng kiểu cấu hình NAT và OSPF cho phần kết nối Internet và DMZ.
