# 02 - Phân tích yêu cầu (Bước 1)

## 1. Đề bài và cách hiểu

| Yêu cầu của đề | Cách hiểu và quyết định thiết kế |
|---|---|
| Trụ sở TP.HCM: 2 tòa A, B, mỗi tòa 5 tầng, mỗi tầng 10 phòng | 100 phòng. Mỗi tầng một tủ viễn thông (IDF), mỗi tòa một tủ chính (MDF) |
| 600 máy trạm, 10 server | Tòa A 290, tòa B 310 máy trạm; 7 server trong server farm và 3 server trong DMZ |
| Phòng dữ liệu và phòng đi cáp riêng, cách tòa nhà 50 m | Data center (DC) đặt riêng, đặt core, firewall, server farm; cáp quang đa mode OM4 từ DC tới MDF hai tòa, hai tuyến vật lý khác nhau |
| Khoảng 12 thiết bị mạng (hoặc nhiều hơn nếu có thiết bị bảo mật) | 12 thiết bị lõi: 2 edge router, 2 firewall, 2 core, 4 distribution, 2 WLC. Switch access (26 chiếc) tính riêng vì số cổng cho 600 máy không thể gói trong 12 thiết bị |
| Phủ sóng WiFi toàn bộ | 60 AP (30 mỗi tòa), hai SSID, điều khiển bởi WLC |
| GPON và 1/10/40 GbE | GPON dùng cho nhánh mật độ thấp (camera ngoài trời, ki-ốt, phòng chờ); 1 GbE tới máy trạm, 10 GbE uplink access và tới server, 40 GbE giữa distribution và core |
| VLAN theo khoa phòng | 51 VLAN toàn hệ thống (xem `generated/ip-plan.md`) |
| WAN: 2 đường thuê riêng tới 2 chi nhánh | Mỗi chi nhánh một đường thuê riêng L2 đối xứng, mã hóa IPsec trên đường thuê riêng; SD-WAN và MPLS được so sánh ở tài liệu 04 |
| Internet: 2 DSL cân bằng tải, mọi lưu lượng đi qua trụ sở | Hai đường Internet vào hai edge router riêng. Tính toán cho thấy DSL không đủ băng thông nên đề xuất cáp quang (tài liệu 04) |
| Firewall, IPS/IDS, phát hiện phishing | NGFW dạng cặp HA kèm IPS, lọc URL/DNS; cổng email gateway ở DMZ phát hiện phishing |
| HA, mở rộng | Mọi tầng lõi đều có cặp dự phòng; khối VLAN dự phòng; cổng uplink dự phòng 30% |
| VPN site-to-site và VPN người làm việc từ xa | Site-to-site: IPsec trên đường thuê riêng giữa R-WAN và router chi nhánh. Remote access: Easy VPN trên EDGE1, chỉ truy cập được HIS |
| Hệ thống camera giám sát | VLAN camera riêng, NVR trong server farm, chỉ camera được phép nói chuyện với NVR |
| Chi nhánh DBP, BHTQ: 2 tầng, 260 máy, 2 server, từ 5 thiết bị mạng | Mỗi chi nhánh 1 router, 9 switch access, 14 AP, 2 server cục bộ |

Phần mô phỏng Packet Tracer là tập con của thiết kế thật (xem tài liệu 05): giữ đủ lớp mạng, định tuyến, NAT, ACL, VPN; thay 13 switch access mỗi tòa bằng một switch đại diện.

## 2. Phân tích cấu trúc

Mạng 3 lớp rút gọn:

- **Access** trên từng tầng: 48 cổng 1 GbE PoE+, uplink 10 GbE lên hai distribution.
- **Distribution** mỗi tòa một cặp, chạy HSRP làm default gateway cho VLAN của tòa; chia tải bằng cách distribution 1 là active cho nửa số VLAN, distribution 2 cho nửa còn lại; STP root khớp với HSRP active.
- **Core** một cặp tại DC, định tuyến OSPF area 0 tới distribution, WAN router và firewall; chứa HSRP cho VLAN WiFi và VLAN quản trị lõi.
- **Firewall** tách 4 vùng: outside (hai đường Internet), inside (campus), servers (server farm), DMZ.
- **Edge** hai router, mỗi router một nhà mạng, thực hiện PAT và static NAT.

Lý do không dùng collapsed core: hai tòa cách DC 50 m và có 26 switch access; distribution theo tòa giữ lưu lượng broadcast và STP trong từng tòa, giảm số uplink cần kéo về DC (4 distribution thay vì 26 switch).

## 3. Danh sách khảo sát (checklist)

Việc cần làm tại công trình trước khi chốt thiết kế:

1. Bản vẽ kiến trúc từng tầng: vị trí 10 phòng, tường chịu lực, trần giả, hộp kỹ thuật (shaft).
2. Chiều dài thực tế từ tủ IDF tới phòng xa nhất; khoảng cách phải nhỏ hơn 90 m cho cáp ngang.
3. Tuyến cáp giữa DC và hai tòa: ống chôn hiện có, độ sâu, hai tuyến vật lý tách biệt.
4. Vị trí tủ IDF mỗi tầng và MDF mỗi tòa: diện tích, ổ cắm điện, UPS, điều hòa.
5. Công suất điện và UPS cho DC: tải server, switch, firewall; thời gian lưu điện mong muốn.
6. Sơ đồ phòng khám: số máy trạm, thiết bị y tế (loại, giao thức, cổng), số camera và góc đặt.
7. Số lượng ca chụp CT, MRI, X-quang mỗi ngày và kích thước ca trung bình (cho PACS).
8. Vật liệu tường ảnh hưởng sóng WiFi (phòng X-quang bọc chì, phòng mổ); khảo sát site survey WiFi.
9. Nhà mạng nào có tuyến cáp tới địa chỉ trụ sở và hai chi nhánh; thời gian lắp đặt, SLA.
10. Yêu cầu hồi phục (RTO/RPO) của HIS và PACS để chọn kiến trúc sao lưu.
11. Chính sách bảo mật hiện hành của bệnh viện và yêu cầu theo TT 54/2017/TT-BYT.
12. Danh sách ứng dụng cần truy cập từ xa và đối tượng được VPN.
13. Danh sách thiết bị khách mang vào: số lượng ước tính mỗi giờ cao điểm.
14. Kế hoạch mở rộng trong 5 năm: tòa mới, khoa mới, số giường.
15. Yêu cầu phòng cháy chữa cháy cho phòng máy (khí sạch, cảm biến nhiệt ẩm).

## 4. Khu vực tải cao

| Khu vực | Lý do | Biện pháp |
|---|---|---|
| Tiếp đón và ngoại trú (tầng 1 và 2 tòa A) | Giờ cao điểm 9-11 giờ, nhiều máy trạm và khách chờ | VLAN riêng, uplink 10 GbE, AP mật độ cao ở sảnh |
| Chẩn đoán hình ảnh (tầng 4 tòa A) | Ca chụp CT/MRI rất lớn, đọc phim đồng thời | VLAN riêng, uplink 10 GbE chuyên dụng, QoS cho DICOM |
| Xét nghiệm (tầng 3 tòa A) | Máy phân tích đẩy kết quả liên tục về LIS | Thiết bị y tế ở VLAN riêng, ACL chỉ cho phép tới LIS |
| Cấp cứu (tầng 1 tòa B) | Cần độ sẵn sàng cao nhất, không chấp nhận mất kết nối | Switch access có nguồn dự phòng, hai uplink về hai distribution |
| Server farm và DMZ | Mọi truy vấn HIS, PACS, camera đi qua | Firewall 10 GbE, switch ToR dự phòng, LACP |
| Camera giám sát | 92 camera ghi liên tục 368 Mbps | VLAN riêng, NVR cục bộ, không đi qua WAN |
| Liên kết WAN | Dữ liệu HIS và PACS của chi nhánh | Đường thuê riêng đối xứng, QoS ưu tiên HIS |

## 5. Thiết kế WiFi

- **Số lượng AP**: 30 mỗi tòa (6 AP mỗi tầng, tăng ở sảnh tầng 1 và phòng chờ), 14 AP mỗi chi nhánh. Đây là giả định để lập dự toán; số chính xác phải theo kết quả site survey.
- **SSID nhân viên** (VLAN 320, 802.1X qua RADIUS/AD): truy cập tài nguyên theo vai trò.
- **SSID khách và bệnh nhân** (VLAN 330): captive portal, client isolation, giới hạn 8 Mbps xuống và 2 Mbps lên mỗi thiết bị, ACL chặn mọi mạng nội bộ (`ACL-GUEST`), chỉ cho phép DNS tới server DNS và đi ra Internet.
- **WLC** một cặp tại DC, các AP dùng CAPWAP về WLC; tại chi nhánh dùng chế độ chuyển mạch cục bộ để lưu lượng khách không phải đi qua WAN.
- Camera và thiết bị y tế không kết nối WiFi khách; thiết bị y tế không dây (nếu có) dùng SSID riêng, VLAN riêng (đề xuất bổ sung ở giai đoạn sau).

## 6. Server farm, DMZ và firewall

Vùng và mức bảo mật trên firewall:

| Vùng | Mức | Thành phần | Chính sách |
|---|---|---|---|
| outside1, outside2 | 0 | Hai đường Internet qua EDGE1, EDGE2 | Mặc định chặn; chỉ mở cổng 80, 443 tới portal, cổng 25 tới mail gateway, HTTPS từ VPN pool tới HIS, ICMP trả lời |
| dmz | 50 | Portal, mail gateway, proxy VPN | Chỉ portal gọi được HIS cổng 8443; chặn mọi truy cập vào mạng nội bộ |
| servers | 90 | HIS, PACS, LIS, AD/DNS, file, NMS, NVR, sao lưu | Chỉ NMS được giám sát SNMP/ICMP tới thiết bị; server ra Internet chỉ HTTP/HTTPS/NTP |
| inside | 100 | Toàn campus và chi nhánh | Được đi ra mọi vùng thấp hơn |

Lưu lượng WiFi khách đi qua ACL ở lớp core trước khi tới firewall, nên không có đường từ khách tới máy trạm.

IPS/IDS đặt ngay sau firewall (inline hoặc module trên NGFW), giám sát hai hướng từ outside và DMZ. Phát hiện phishing: cổng email gateway ở DMZ quét URL và tệp đính kèm, firewall lọc DNS/URL theo danh mục. Các chức năng này không có trong Packet Tracer nên chỉ được thể hiện trong thiết kế và báo cáo.
