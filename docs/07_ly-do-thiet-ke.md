# 07 - Lý do của từng quyết định thiết kế

Tài liệu này trả lời câu hỏi vì sao thiết kế như vậy, dành cho lúc bảo vệ và lúc viết báo cáo. Mỗi mục gồm quyết định, phương án đã cân nhắc, lý do và điều phải đánh đổi. Các con số lấy từ tài liệu 02 đến 04 và `generated/`; chỗ nào là giả định thì ghi rõ.

## 1. Cấu trúc tổng thể

### Mạng 3 lớp rút gọn: access, distribution, core

- **Quyết định**: access trên từng tầng, một cặp distribution cho mỗi tòa, một cặp core đặt tại phòng dữ liệu (DC).
- **Phương án khác**: collapsed core (access nối thẳng về core).
- **Lý do**: có 26 switch access và hai tòa cách DC 50 m. Nếu nối thẳng, phải kéo 26 cặp uplink về DC và mọi broadcast, STP của cả khuôn viên nằm chung một miền. Có distribution theo tòa thì chỉ cần 4 distribution nối về core, và lỗi vòng lặp ở tòa này không lan sang tòa kia.
- **Đánh đổi**: thêm 4 thiết bị L3 phải mua và cấu hình.

### Mọi tầng lõi đều là một cặp

- **Quyết định**: edge, firewall, core, distribution, WLC, mỗi loại hai thiết bị; access có hai uplink về hai distribution.
- **Lý do**: bệnh viện chạy 24/7, thông tư yêu cầu thời gian phục hồi ngắn. Cặp thiết bị loại bỏ điểm hỏng đơn trên đường đi của dữ liệu.
- **Đánh đổi**: chi phí thiết bị gấp đôi ở phần lõi. Đây là chi phí chấp nhận được vì số thiết bị lõi chỉ khoảng 12, phần đắt nhất vẫn là 26 switch access và cáp.

### Phòng dữ liệu tách riêng khỏi hai tòa

- **Quyết định**: core, firewall, server farm, DMZ đặt tại DC; hai tuyến cáp quang vật lý khác nhau tới mỗi tòa.
- **Lý do**: đề cho DC riêng cách tòa 50 m. Đặt thiết bị quan trọng ở một nơi dễ kiểm soát ra vào, điện, làm mát. Hai tuyến cáp tách biệt để một lần đào đứt cáp không làm mất cả tòa.

## 2. Chuyển mạch và dự phòng gateway

### HSRP chia tải xen kẽ, STP root khớp với HSRP

- **Quyết định**: distribution 1 là active cho các VLAN thứ tự lẻ, distribution 2 cho các VLAN thứ tự chẵn; STP root của VLAN nào đặt ở đúng thiết bị là HSRP active của VLAN đó.
- **Phương án khác**: một distribution active cho tất cả, bên kia chỉ chờ.
- **Lý do**: cách chia xen kẽ dùng được cả hai uplink và cả hai thiết bị ở trạng thái bình thường. Nếu STP root và HSRP active lệch nhau, gói tin đi lên switch này rồi vòng sang switch kia mới ra gateway, tốn băng thông liên kết giữa hai distribution.
- **Đánh đổi**: cấu hình phức tạp hơn; số nhóm HSRP đánh số tuần tự theo từng cặp thiết bị (1 đến N) vì HSRP phiên bản 1 chỉ cho tới 255.

### DHCP chia hai nửa dải (split scope)

- **Quyết định**: mỗi VLAN có hai nửa dải cấp phát đặt ở hai thiết bị.
- **Lý do**: một thiết bị hỏng thì thiết bị còn lại vẫn cấp địa chỉ cho máy mới. Nếu chỉ một DHCP server, mạng vẫn chạy nhưng máy mới bật lên không có IP.
- **Đánh đổi**: mỗi nửa dải nhỏ hơn, nên mỗi subnet đã được cộng 20% dự phòng để không bị thiếu.

### Rapid-PVST thay vì STP gốc

- **Lý do**: hội tụ trong vài giây thay vì vài chục giây; với cấu trúc hai uplink mỗi access, đây là điều kiện để dự phòng có ý nghĩa.

## 3. Định tuyến

### OSPF area 0 duy nhất

- **Lý do**: mạng chỉ có vài chục router và switch L3, một area là đủ và đơn giản nhất để kiểm tra. Nhiều area chỉ có ích khi bảng định tuyến lớn đến mức cần tóm tắt route, ở đây chưa cần. OSPF hội tụ nhanh, là chuẩn mở và Packet Tracer hỗ trợ.
- **Chi tiết**: mọi SVI đặt passive để không gửi hello ra phía máy trạm.

### Route mặc định bắt nguồn từ CORE1 và hai route bằng nhau trên firewall

- **Quyết định**: firewall có hai route mặc định bằng nhau qua EDGE1 và EDGE2 (ECMP); CORE1 quảng bá route mặc định vào OSPF bằng `default-information originate`.
- **Lý do**: đề yêu cầu cân bằng tải hai đường Internet và mọi lưu lượng đi qua trụ sở. Đặt ECMP tại firewall cho phép một nơi duy nhất thấy cả hai đường, áp chính sách thống nhất và chia tải. Mất link tới một EDGE thì route tương ứng biến mất, lưu lượng tự chuyển sang EDGE còn lại.
- **Giới hạn đã biết**: nhà mạng hỏng ngầm (link vẫn lên nhưng không ra Internet) chưa được phát hiện. Cách sửa là IP SLA hoặc giám sát đường đi, ghi ở tài liệu 06.

### Lưu lượng chi nhánh luôn đi qua trụ sở (hub-and-spoke)

- **Lý do**: đề yêu cầu mọi lưu lượng Internet đi qua trụ sở, nên chính sách bảo mật và NAT chỉ phải quản lý ở một nơi. DBP đi BHTQ cũng qua trụ sở vì không có đường nối trực tiếp.
- **Đánh đổi**: độ trễ DBP tới BHTQ cao hơn đường thẳng. Lưu lượng này nhỏ (tài liệu 04) nên chấp nhận được.

## 4. Địa chỉ IP

### Mỗi site một khối /16, VLSM bên trong

- **Quyết định**: 10.10.0.0/16 trụ sở, 10.20.0.0/16 DBP, 10.30.0.0/16 BHTQ; trong trụ sở tòa A dùng 10.10.0.0/20, tòa B 10.10.16.0/20, dịch vụ dùng chung 10.10.32.0/20.
- **Lý do**: nhìn địa chỉ biết ngay thuộc site nào, tòa nào, nên ACL và bảng định tuyến gọn (một dòng cho cả một site). Khối /16 cho chỗ mở rộng vì trụ sở mới dùng dưới 10%.
- **Phương án khác**: một khối lớn cấp liên tục. Gọn lúc đầu nhưng khó tóm tắt route và khó thêm tòa mới.

### Liên kết point-to-point dùng /30 từ 172.16.0.0/16, loopback riêng

- **Lý do**: /30 vừa đủ hai địa chỉ, không phí. Tách khỏi 10.x để địa chỉ hạ tầng không lẫn với địa chỉ người dùng, giúp ACL dễ viết. Loopback làm router-id OSPF để id không đổi khi một cổng hỏng.

### Địa chỉ công cộng mô phỏng lấy từ dải tài liệu (203.0.113.0/29, 198.51.100.0/29, 192.0.2.0/24)

- **Lý do**: các dải này được dành riêng để làm ví dụ và không bao giờ được định tuyến trên Internet thật, nên mô phỏng không đụng địa chỉ thật.

### Quy ước `.1` là gateway ảo, `.2` và `.3` là hai distribution

- **Lý do**: máy trạm luôn thấy gateway cùng một địa chỉ bất kể thiết bị nào đang active; quy ước cố định giúp đọc cấu hình và gỡ lỗi nhanh.

## 5. VLAN, WiFi và phân vùng bảo mật

### 51 VLAN, tách theo chức năng

- **Lý do**: thiết bị y tế, camera, khách, quản trị, mỗi nhóm có yêu cầu bảo mật khác nhau nên phải tách broadcast domain để áp ACL riêng. Đề yêu cầu VLAN theo khoa phòng; khu vực tải cao có VLAN riêng để áp QoS và uplink riêng.

### Hai SSID, khách tách hẳn

- **Quyết định**: SSID nhân viên dùng 802.1X; SSID khách và bệnh nhân dùng captive portal, client isolation, giới hạn băng thông, và bị ACL chặn mọi dải nội bộ.
- **Lý do**: khách mang thiết bị không kiểm soát được vào mạng; nếu cùng VLAN với nhân viên thì một máy nhiễm mã độc có thể quét thẳng vào HIS.
- **Đặt ACL ở core**: lưu lượng khách bị lọc trước khi tới firewall, nên không có đường nào từ khách tới máy trạm.
- **Chi nhánh**: dùng chế độ chuyển mạch cục bộ để lưu lượng khách không chạy qua đường thuê riêng và không ăn băng thông của HIS.

### Firewall bốn vùng (outside 0, dmz 50, servers 90, inside 100)

- **Lý do**: mức tin cậy cao được đi ra mức thấp mặc định, chiều ngược lại phải mở rule rõ ràng. Server nội bộ (HIS, PACS) ở vùng riêng nên kể cả khi DMZ bị chiếm cũng không có đường vào. Portal ở DMZ chỉ được gọi HIS đúng một cổng, vì portal là thứ tiếp xúc Internet nên coi là có thể bị tấn công.
- **Phương án khác**: một firewall hai vùng (trong, ngoài) và đặt cả portal vào mạng trong. Đơn giản hơn nhưng không an toàn cho dữ liệu bệnh nhân.

### Camera và thiết bị y tế bị khóa bằng ACL

- **Lý do**: camera và thiết bị y tế thường chạy firmware cũ, khó vá, nên coi là không đáng tin. ACL-CCTV chỉ cho camera nói chuyện với NVR; ACL-MEDDEV chỉ cho thiết bị y tế tới HIS, PACS, LIS. Tại chi nhánh, NVR là server cục bộ chứ không phải NVR ở trụ sở, để camera không phải đi qua WAN.
- **Giới hạn đã biết**: các ACL này mới lọc chiều đi ra từ VLAN, chưa lọc chiều từ máy nhân viên vào VLAN. Cách bổ sung ghi ở tài liệu 06.

## 6. Cáp và thiết bị

### Cat6A cho cáp ngang, OM4 cho riser và liên tòa

- **Lý do**: Cat6A chạy 10G tới 100 m; Cat6 chỉ khoảng 55 m với 10G nên chọn Cat6A để tuổi thọ cáp (thường dài hơn tuổi thọ switch) không bị nâng cấp lại. OM4 đủ cho 40G ở khoảng cách dưới 50 m với chi phí thấp hơn đơn mode.
- **Đánh đổi**: Cat6A đắt và cứng hơn Cat6.

### Tốc độ liên kết: 1G máy trạm, 10G uplink access, 40G distribution lên core

- **Lý do** (số trong tài liệu 04): 48 cổng 1G chia 20 là 2,4 Gbps nên 1 đường 10G là đủ và còn dư; tổng các uplink xuống access của một distribution là 13 x 10G chia 4 là 32,5 Gbps nên cần 2 x 40G lên core. Chọn theo tính toán, không chọn cao hơn mức cần.

### Firewall chọn NGFW từ 4 Gbps khi bật IPS

- **Lý do**: tổng lưu lượng qua firewall khoảng 1,9 Gbps. Khi bật IPS và SSL inspection hiệu năng giảm mạnh so với số quảng cáo, nên chọn dư hơn hai lần.

### Số lượng access switch và AP

- **Số switch**: lấy số cổng cần của mỗi tòa (A 584, B 608, đã cộng 20% dự phòng) chia cho 48 cổng, làm tròn lên, ra 13 mỗi tòa.
- **Số AP**: 6 AP mỗi tầng mỗi tòa là giả định để lập dự toán, số thật phải theo site survey.

## 7. Internet và WAN

### Đề xuất cáp quang 1 Gbps thay cho DSL

- **Lý do**: nhu cầu sau 5 năm là khoảng 600 Mbps xuống và 100 Mbps lên, DSL chỉ cho vài chục Mbps và bất đối xứng, thiếu hơn một bậc độ lớn. 1 Gbps mỗi đường là mức duy nhất mà một đường hỏng thì đường còn lại vẫn gánh đủ tải; 500 Mbps mỗi đường thì khi mất một đường thiếu khoảng 100 Mbps lúc cao điểm.
- **Giữ nguyên ý đề**: vẫn hai đường, vẫn chia tải. Báo cáo nêu rõ điểm đề xuất khác chữ của đề và lý do bằng bảng so sánh.

### Đường thuê riêng L2 đối xứng cho chi nhánh, không dùng MPLS hay SD-WAN làm đường chính

- **Lý do**: băng thông đối xứng, riêng tư, có SLA, chi phí dự đoán được. HIS và PACS nhạy với độ trễ và mất gói, không nên đi trên Internet công cộng.
- **Đề xuất 500 Mbps mỗi chi nhánh** (tối thiểu 200 Mbps): nhu cầu cao điểm khoảng 154 Mbps xuống và 42 Mbps lên, cộng sao lưu ban đêm, cộng chỗ cho QoS và nâng cấp.
- **SD-WAN**: đưa vào hướng phát triển, dùng đường băng rộng giá rẻ làm dự phòng.

### Mã hóa IPsec trên cả đường thuê riêng

- **Lý do**: đường thuê riêng là riêng tư về mặt tổ chức nhưng không mã hóa, trong khi dữ liệu là hồ sơ bệnh nhân. Mã hóa chống nghe lén trong hạ tầng nhà mạng và là yêu cầu thường gặp khi đánh giá an toàn thông tin y tế.
- **Đánh đổi**: tốn CPU router và giảm MTU; hiệu năng router chọn phải đủ cho 500 Mbps.

### VPN người làm việc từ xa: Easy VPN trên EDGE1, chỉ vào được HIS

- **Lý do**: nguyên tắc ít quyền nhất. Người làm từ xa cần HIS, không cần cả mạng nội bộ. Dải địa chỉ VPN nằm riêng (192.168.99.10 đến 60) để firewall nhận ra và chỉ mở HTTPS từ dải này tới HIS; NAT edge loại trừ dải này để lưu lượng VPN không bị dịch địa chỉ.

### NAT đặt tại EDGE

- **Quyết định**: PAT cho dải nội bộ ra Internet và static NAT cho portal, mail gateway tại EDGE.
- **Lý do**: địa chỉ công cộng thuộc từng nhà mạng nên việc dịch địa chỉ gắn với router đang nối nhà mạng đó. Firewall ở trong chỉ phải xử lý địa chỉ riêng.
- **Giới hạn đã biết**: dịch vụ công bố qua hai nhà mạng có vấn đề định tuyến bất đối xứng, nên chỉ công bố một địa chỉ và dùng DNS cho dự phòng.

## 8. Mô phỏng Packet Tracer

### Mô phỏng là tập con của thiết kế thật

- **Quyết định**: giữ đủ các lớp, định tuyến, NAT, ACL, VPN; thay 13 switch access mỗi tòa bằng một switch đại diện; chi nhánh dùng 2 trong 9 switch; một firewall thay cho cặp HA.
- **Lý do**: Packet Tracer không có đủ tính năng (IPS, lọc URL, GPON) và hàng chục switch access cùng kiểu chỉ lặp lại cấu hình mà không cho kiểm chứng thêm điều gì. Mô phỏng nhỏ hơn thì chạy nhanh hơn và dễ kiểm thử bằng ping, traceroute.
- **Cách bảo đảm không mất ý nghĩa**: tài liệu 05 ghi rõ phần nào được mô phỏng, phần nào chỉ là thiết kế.

### Thiết bị Packet Tracer được chọn

- **Quyết định**: Cisco 2911 cho router, ASA 5506-X cho firewall, Catalyst 3650-24PS cho core và distribution, 2960-24TT cho access.
- **Lý do**: là các model có sẵn trong Packet Tracer và hỗ trợ đúng các tính năng cần (routing L3 trên switch, zone-based ASA, crypto).
- **Chưa chắc**: HSRP trên 3650, ECMP trên ASA, Easy VPN client, WLC với LAP, giấy phép securityk9 trên 2911. Phải kiểm chứng ở bước 4; nếu không chạy thì đổi thiết bị hoặc ghi vào báo cáo là chỉ có trong thiết kế.

## 9. Cách tổ chức repo

### Sinh tài liệu và cấu hình từ một mô hình dữ liệu duy nhất

- **Quyết định**: `tools/model.py` và `tools/topology.py` là nguồn dữ liệu; `tools/design.py` kiểm tra và sinh `docs/generated/` cùng `Configurations/`.
- **Lý do**: bảng IP, bảng đấu nối và 22 file cấu hình phải khớp nhau tuyệt đối; viết tay dễ lệch (trùng subnet, sai gateway). Một nguồn dữ liệu cộng kiểm tra tự động (không trùng VLAN và subnet, đủ chỗ cho số host, tổng máy trạm khớp 600 và 260) loại cả nhóm lỗi này. Đổi địa chỉ chỉ sửa một chỗ rồi chạy lại.
- **Đánh đổi**: không sửa tay file được sinh; người mới phải biết chạy lệnh.

### Sơ đồ là ảnh PNG, không phải mã để dựng

- **Lý do**: ảnh xem được ngay trên GitHub, trong báo cáo và slide mà không cần trình duyệt hay công cụ nào; mã dựng sơ đồ là một phần phải bảo trì mà không thêm giá trị cho người đọc.
- **Đánh đổi**: đổi topology thì ảnh không tự cập nhật, phải dựng lại.

### Tài liệu tiếng Việt, giữ thuật ngữ tiếng Anh

- **Lý do**: báo cáo nộp bằng tiếng Việt; thuật ngữ như HSRP, VLAN, ACL giữ nguyên để khớp với tài liệu hãng và với cấu hình thiết bị.
