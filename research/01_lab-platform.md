# Nghiên cứu 01 - Nền tảng lab (quyết định quan trọng nhất)

Ngày nghiên cứu: 27/10/2026. Mức tin cậy ghi ở cuối mỗi mục. Nguồn xem file 05_sources.md.

## 1. Vấn đề

Đề yêu cầu EVE-NG/GNS3/CML với image Cisco vIOS/vIOS-L2, khuyến nghị CPU 8 core có VT-x, RAM 16GB, nested virtualization. Máy dùng để làm là MacBook Apple Silicon (ARM). Topology theo hướng dẫn lab của đề có khoảng 11 node: HQ (1 core, 2 distribution, 1 edge) = 4, Hanoi (1 router, 2 switch) = 3, Da Nang (1 router, 1 switch) = 2, ISP = 1, automation node = 1.

## 2. Các phương án

### A. Máy x86 riêng (cloud VM hoặc PC) chạy EVE-NG/GNS3
- Đây là đường đề dự kiến. Nested virtualization là điều kiện then chốt với image dạng VM (vIOS, vIOS-L2).
- Tradeoff: tốn tiền cloud hoặc phải mượn PC; thao tác qua web UI nên Mac chỉ làm client.
- Chưa kiểm tra được trong lần nghiên cứu này: yêu cầu phần cứng chính thức của EVE-NG (trang system requirement chỉ có mục lục, chưa đọc được các trang con) và giá cloud cụ thể.

### B. Cisco Modeling Labs Free
- Miễn phí, không cần license, không giới hạn thời gian, nhưng chạy tối đa 5 node cùng lúc (Unmanaged Switch và External Connector không tính).
- Image đi kèm: IOL, IOL-L2, ASAv, Ubuntu, Alpine, Desktop. Image Cisco chỉ được cấp phép dùng trong CML.
- Cài trên bare metal hoặc VM VMware (x86). Trang chính thức không đề cập Apple Silicon.
- Cần tài khoản Cisco.com đầy đủ thông tin; telemetry luôn bật.
- Kết luận: 5 node không đủ cho topology 11 node chạy cùng lúc. Có thể dùng để thử từng site riêng lẻ, nhưng không thể demo toàn bộ cùng lúc. Nếu trường có license CML đầy đủ thì khác.

### C. Containerlab trên Mac (OrbStack/Linux VM)
- Containerlab trên Apple Silicon chạy trong VM Linux; image ARM64 native chạy tốt nhất.
- ARM64 có sẵn: FRR, Nokia SR Linux (preview), cRPD (chỉ control plane). Arista cEOS ARM chưa xác nhận đã phát hành.
- Image chỉ có x86 (cEOS x64, Cisco IOL) chạy qua Rosetta được, nhưng có phạt hiệu năng và có thể làm một số node không chạy.
- VM-based (vrnetlab) cần nested virtualization, bài viết giới hạn ở chip M3 trở lên với macOS 15 trở lên.
- Bài hướng dẫn GNS3 trên Mac của nerdydrunk dựng một máy Ubuntu amd64 trong OrbStack rồi cài gns3-server và QEMU x86; bài không nói gì về image Cisco.
- Vấn đề lớn: FRR không có HSRP, DHCP snooping, DAI, port security kiểu Cisco; Step 3-4-7 của đề đòi đúng các tính năng này, nên FRR chỉ phù hợp làm router ISP.
- Cập nhật: hướng lấy IOL ra khỏi ISO của CML để chạy trong containerlab bị loại vì vi phạm giấy phép nêu ở mục B. Trên Mac chỉ dùng FRR (ISP, BGP, OSPF) và Packet Tracer; thư mục lab-frr/ chạy trên Docker Desktop.

### D. VMware Fusion trên Apple Silicon
- Fusion trên Apple Silicon chỉ chạy guest Arm 64-bit. Broadcom ghi rõ: không thể chạy hệ điều hành x86 trong VM Fusion trên Mac Apple Silicon.
- Các tính năng cần nested virtualization không hoạt động trong VM trên Apple Silicon (Broadcom nêu cụ thể với Windows).
- Hệ quả: không thể nhập EVE-NG OVA, GNS3 VM hay CML (đều là x86) vào Fusion trên Mac này. Một thread trên VMware Communities cũng kết luận EVE-NG không cài được trên Mac M2 với Fusion; thread trích tài liệu EVE-NG: không có bản ARM, và chip M1/M2/M3 không được hỗ trợ do vấn đề Fusion và nested CPU.
- Fusion vẫn dùng được như nơi chạy một VM Ubuntu Arm64 để cài containerlab, thay cho OrbStack (hướng C). Khi đó vẫn chạy image Arm64 native; image x86 như IOL phải qua emulation trong VM Arm, và độ ổn định chưa được xác minh.
- Chỉ đúng nếu máy là Apple Silicon (môi trường kiểm tra cho thấy kiến trúc aarch64). Nếu là Mac Intel thì Fusion chạy được guest x86, khi đó phương án EVE-NG/GNS3 VM khả thi.

### E. Packet Tracer
- Chỉ khi giảng viên duyệt; đề nói thiếu hỗ trợ một số giao thức (EVPN/BGP).

## 3. Giới hạn tính năng của từng image Cisco (quan trọng cho thiết kế)

| Image | Điều đã xác nhận từ nguồn | Hệ quả cho đề |
|---|---|---|
| IOSv | Layer 2 switching không được hỗ trợ; QoS chưa được kiểm thử/chưa hỗ trợ chính thức; IPsec có; HSRP có trong bảng test (Pass) | Chỉ dùng làm router. Cần xác nhận QoS (Step 8) chạy được |
| IOSvL2 | Không dùng được VLAN 1002-1005, không tagged VLAN 1 trên trunk; tài liệu CML không liệt kê tính năng chi tiết | Dùng làm switch, test từng tính năng trước |
| IOL | Chạy nhẹ hơn IOSv/CSR vì không phải VM đầy đủ; 16 interface Ethernet mỗi image; không MTU tùy chỉnh (cố định 1500); EVPN-VXLAN chạy được (ingress replication tĩnh thì không) | Phù hợp nếu cần EVPN-VXLAN |
| IOL-L2 | EVPN-VXLAN chạy cho kịch bản L2; VLAN interface xuống nếu không có member port up (có thể cần tắt autostate) | Nhớ khi cấu hình SVI/HSRP |
| CSR1000v | Có VXLAN với ingress replication, EVPN chỉ MPLS; không hỗ trợ EVPN với VXLAN | Không dùng cho EVPN-VXLAN |
| Catalyst 8000v | EVPN-VXLAN chạy (khuyến nghị bản 17.16.01a trở lên) nhưng cần Premier license | Khó có license |

Chưa xác nhận được từ nguồn nào đã đọc: LACP/EtherChannel, Rapid PVST+, DHCP snooping, DAI, port security trên IOL-L2/IOSvL2. Tài liệu chính thức của Cisco im lặng về các mục này; cần thử trực tiếp trong lab. Đây là việc đầu tiên cần làm.

## 4. Việc nên làm ngay (feasibility spike, 1 ngày)

1. Hỏi giảng viên/khoa: có server lab, license CML, hoặc image được cấp sẵn không? Nếu có, quyết định xong luôn.
2. Nếu không: thử dựng OrbStack amd64 + containerlab (hoặc GNS3 server) và chạy 2 node IOL-L2 + 1 node IOL, kiểm tra LACP, Rapid PVST+, HSRP, DHCP snooping, DAI.
3. Song song ước lượng chi phí một VM x86 có nested virtualization để dự phòng.
4. Nguồn image: chỉ dùng nguồn hợp pháp (CML Free đi kèm IOL; trường cung cấp). GNS3 nói rõ không cung cấp image hay license IOU.

## 5. Khuyến nghị tạm thời

Cập nhật 29/10/2026: lab thật chạy EVE-NG/GNS3 trên máy x86 của đồng đội (nguồn image hợp pháp vẫn cần hỏi giảng viên). Trên Mac luyện bằng FRR (containerlab trên Docker Desktop) và Packet Tracer. Chưa chốt EVPN-VXLAN cho Step 6; chọn IPsec VTI + BGP làm đường chính, EVPN-VXLAN trình bày ở mức thiết kế trong báo cáo.

Mức tin cậy: trung bình. Thông tin ARM/Rosetta lấy từ bài viết cộng đồng và tài liệu containerlab; chưa tự thử.
