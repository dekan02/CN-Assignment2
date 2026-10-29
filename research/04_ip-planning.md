# Nghiên cứu 04 - Quy hoạch IP (Step 2)

Chỉ ghi nguyên tắc; bảng IP cụ thể được làm ở bước thiết kế (Step 1-2).

## IPv6
- Khuyến nghị phổ biến: mỗi site một /48, mỗi subnet một /64. Một /48 chứa 65.536 subnet /64.
- /48 là prefix nhỏ nhất định tuyến được trên internet, nên mỗi site có thể ra internet trực tiếp.
- Chia theo ranh giới nibble (/48, /52, /56, /60, /64) để dễ đọc và troubleshoot; ví dụ dành /52 hoặc /56 cho từng nhóm chức năng trong site.
- Ví dụ cấu trúc: prefix tổ chức -> /48 site -> /52 hoặc /56 theo chức năng (user, server, IoT, guest, mgmt, link) -> /64 VLAN. Link point-to-point dùng /127 hoặc /64 tùy chính sách; cần chọn và giải thích.
- Dùng địa chỉ tài liệu 2001:db8::/32 trong báo cáo/lab.

## IPv4 VLSM
- Quy trình: liệt kê VLAN và số host cần (kèm dư tăng trưởng tới 2030), sắp xếp từ lớn đến nhỏ, cấp khối liền kề sao cho mỗi site gói được thành một summary.
- Quy mô cần tính: ~2.000 user HQ, ~1.500 Hanoi, ~500 Da Nang, 10.000+ IoT, guest, voice, mgmt, link, loopback.
- Bài toán thiết kế: 10.000+ IoT cần khoảng /18 nếu một vùng (16.382 host) hoặc chia nhiều VLAN IoT theo site; với 4.000+ user nên tách VLAN nhỏ hơn /22 để hạn chế broadcast domain (đề nhắc broadcast storm).
- Dùng RFC1918 (10.0.0.0/8 đủ chỗ), mỗi site một khối summary (ví dụ /16 hoặc /15) để summarization ở edge đơn giản và tránh lãng phí (rubric yêu cầu không "massive IP waste").
- Management: VLAN 99, loopback /32, link point-to-point /30 hoặc /31.
- Lưu ý: địa chỉ mgmt trong đề (192.168.1.x, 2.x, 3.x) chỉ là ví dụ trong starter code; có thể thay bằng plan riêng, nhưng phải khớp inventory.yaml.

## Kiểm tra bắt buộc
- Không overlap giữa mọi subnet (có thể viết script Python ipaddress để kiểm tra, đây cũng là bằng chứng tốt cho báo cáo).
- Mỗi site summarize được thành ít prefix nhất có thể.
- IPv6 có song song trên interface dual-stack (checklist đề yêu cầu GUA).
