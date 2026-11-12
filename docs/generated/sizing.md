# Kết quả tính số lượng thiết bị và uplink

| Khu vực | Máy trạm | AP | Camera | TB y tế | Cổng cần | Cổng + 20% dự phòng | Switch 48 cổng |
|---|---|---|---|---|---|---|---|
| Tòa A | 290 | 30 | 46 | 120 | 486 | 584 | 13 |
| Tòa B | 310 | 30 | 46 | 120 | 506 | 608 | 13 |
| DBP | 260 | 14 | 26 | 40 | 340 | 408 | 9 |
| BHTQ | 260 | 14 | 26 | 40 | 340 | 408 | 9 |

Uplink mỗi switch access: tối thiểu 2.4 Gbps (oversubscription 20:1) nên dùng 1 x 10G tới mỗi distribution.
Distribution tòa A: 13 x 10G xuống access = 130 Gbps, lên core tối thiểu 32.5 Gbps (oversubscription 4:1) nên dùng 2 x 40G.
Distribution tòa B: 13 x 10G xuống access = 130 Gbps, lên core tối thiểu 32.5 Gbps (oversubscription 4:1) nên dùng 2 x 40G.

Luồng camera trụ sở: 368 Mbps liên tục (4 Mbps/camera).
Luồng tới server farm (7 server x 3000 MB/ngày, đã tăng trưởng): 14.9 Mbps.
PACS trụ sở (300 ca/ngày x 400 MB, đã tăng trưởng): 85.3 Mbps cao điểm.
Lưu lượng Internet sau 5 năm: 700 Mbps (hai chiều).
Tổng lưu lượng đi qua firewall (ước tính): 1241.6 Mbps, nhân hệ số an toàn 2 được 2.5 Gbps; chọn NGFW có throughput bật IPS từ 4 Gbps.
