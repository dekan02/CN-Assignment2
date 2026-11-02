# 04 - Lưu lượng và băng thông (Bước 3)

Số liệu do `tools/bandwidth.py` và `tools/sizing.py` tính; kết quả đầy đủ nằm ở `generated/bandwidth.md` và `generated/sizing.md`. Chạy lại bằng `python3 tools/design.py`.

## 1. Giả định

| Mục | Giá trị | Nguồn |
|---|---|---|
| Server | 1000 MB/ngày tải xuống, 2000 MB/ngày tải lên mỗi server | Đề |
| Máy trạm | 500 MB/ngày xuống, 100 MB/ngày lên | Đề |
| Thiết bị WiFi khách | 500 MB/ngày | Đề |
| Giờ cao điểm | 80% lưu lượng ngày dồn vào 3 giờ (9-11 và 15-16) | Đề |
| Tăng trưởng | 20% sau 5 năm, nhân hệ số 1,2 | Đề |
| Số thiết bị khách đồng thời | 300 ở trụ sở, 120 mỗi chi nhánh | Giả định của nhóm, bằng cỡ subnet khách |
| Lưu lượng HIS của chi nhánh về trụ sở | 40 MB/ngày mỗi người dùng | Giả định |
| PACS chi nhánh gửi về trụ sở | 60 ca/ngày, 300 MB/ca | Giả định, theo khoảng kích thước ca ở tài liệu 01 |
| Xem camera từ xa | 8 Mbps mỗi chi nhánh | Giả định |

## 2. Công thức

Tốc độ cao điểm (Mbps) = MB mỗi ngày x 8 x 0,8 / (3 x 3600).

Ví dụ một máy trạm tải xuống: 500 x 8 x 0,8 / 10800 = 0,296 Mbps. 600 máy trạm tải xuống 177,8 Mbps; 10 server tải xuống 2,96 Mbps; 300 thiết bị khách 88,9 Mbps; cộng lại 269,6 Mbps (bảng dưới tính chính xác theo từng site).

## 3. Kết quả

| Site | Internet xuống (Mbps) | Internet lên (Mbps) | Về trụ sở xuống (Mbps) | Về trụ sở lên (Mbps) |
|---|---|---|---|---|
| HCM | 272,6 | 47,4 | không áp dụng | không áp dụng |
| DBP | 113,8 | 17,8 | 14,2 | 16,8 |
| BHTQ | 113,8 | 17,8 | 14,2 | 16,8 |

Tổng Internet hiện tại: 500,1 Mbps xuống, 83,0 Mbps lên. Sau 5 năm: 600,2 Mbps xuống, 99,6 Mbps lên.

Đường thuê riêng tới mỗi chi nhánh sau 5 năm: khoảng 154 Mbps xuống, 42 Mbps lên.

## 4. Băng thông nội bộ và thiết bị

| Hạng mục | Kết quả |
|---|---|
| Camera trụ sở | 92 camera x 4 Mbps = 368 Mbps ghi liên tục tới NVR |
| Máy trạm tới server farm | 720 Mbps (giả định 1 Mbps mỗi máy, đã nhân tăng trưởng) |
| PACS trụ sở | 57 Mbps cao điểm (200 ca/ngày, 400 MB/ca) |
| Tổng qua firewall | khoảng 1,9 Gbps; chọn NGFW bật IPS tối thiểu 4 Gbps |
| Uplink access | 48 cổng 1 G chia 20 bằng 2,4 Gbps cần; dùng 1 x 10G tới mỗi distribution |
| Distribution lên core | 13 x 10G xuống access, chia 4 bằng 32,5 Gbps; dùng 2 x 40G |
| Số switch access | A 13, B 13, mỗi chi nhánh 9 |

## 5. Lựa chọn đường Internet

Tổng băng thông Internet cần sau 5 năm: 600 Mbps xuống, 100 Mbps lên, ước tính theo chuẩn của đề.

| Phương án | Băng thông khả dụng | Đánh giá |
|---|---|---|
| 2 đường DSL như đề | Khoảng vài chục Mbps mỗi đường, bất đối xứng (kiến thức chung, chưa kiểm chứng bằng nguồn cụ thể) | Không đáp ứng: thiếu hơn một bậc độ lớn |
| 2 cáp quang 500 Mbps | Mỗi đường 500 Mbps | Đủ khi hai đường cùng chạy, nhưng khi một đường hỏng thì thiếu 100 Mbps cao điểm sau 5 năm |
| 2 cáp quang 1 Gbps (đề xuất) | Mỗi đường 1 Gbps | Một đường đủ gánh toàn bộ tải sau 5 năm, nên dự phòng không suy giảm chất lượng |

Đề xuất: hai đường Internet doanh nghiệp 1 Gbps từ hai nhà mạng khác nhau, đi hai tuyến khác nhau; chia tải giữa hai đường bằng ECMP trên firewall thật; trong Packet Tracer ECMP của ASA làm NAT và đường về lệch nên mô phỏng chia theo đích (hai tuyến /1, mỗi tuyến có tuyến dự phòng ở đường còn lại), xem tài liệu 05. Nếu bắt buộc theo chữ của đề (DSL), báo cáo ghi rõ đây là điểm không đủ và nêu lý do bằng bảng trên.

Chi phí thuê bao: không tìm được giá công khai cho đường thuê riêng và Internet doanh nghiệp 1 Gbps tại Việt Nam. Bảng giá tham khảo đọc được (ngày đăng không rõ) cho gói 500 Mbps khoảng 1,5 đến 2 triệu đồng mỗi tháng và 1 Gbps khoảng 2,5 đến 3 triệu đồng mỗi tháng; đây chỉ là ước lượng và phải được thay bằng báo giá của nhà mạng trước khi nộp.

## 6. Chọn đường thuê riêng cho chi nhánh

Nhu cầu khoảng 154 Mbps xuống và 42 Mbps lên sau 5 năm, cộng nhu cầu sao lưu và sao chép dữ liệu ban đêm. Đề xuất đường thuê riêng đối xứng 500 Mbps mỗi chi nhánh: đủ cho tải cao điểm, cho phép QoS ưu tiên HIS và thoại, và còn chỗ nâng cấp. Mức tối thiểu chấp nhận được là 200 Mbps đối xứng.

## 7. Các phương án WAN, chi phí và phân tích phương án chọn

Đề yêu cầu liệt kê các phương án kết nối chi nhánh, đưa chi phí và phân tích ưu nhược điểm của phương án chọn. Không tìm được bảng giá công khai tại Việt Nam cho kênh thuê riêng hay MPLS (trang BKNS chỉ nêu dải băng thông 2 Mbps đến 10 Gbps, trang Viettel chỉ dẫn số liên hệ), nên cột chi phí dùng tỷ lệ tương đối từ một khảo sát thị trường Bắc Mỹ ngày 8/4/2026 (Lightyear): MPLS 1 Gbps khoảng 1,44 USD mỗi Mbps mỗi tháng, đường Internet chuyên dụng (DIA) 1 Gbps khoảng 0,97 USD, băng rộng 1 Gbps khoảng 0,31 USD, SD-WAN quản lý trọn gói từ khoảng 100 USD mỗi site mỗi tháng. Tỷ lệ này chỉ để so sánh giữa các phương án; con số thật phải thay bằng báo giá của Viettel, VNPT hoặc FPT.

| Phương án | Chi phí tương đối | Ưu điểm | Nhược điểm |
|---|---|---|---|
| Kênh thuê riêng L2 đối xứng (chọn) | Trung bình đến cao, giá cố định theo băng thông | Đối xứng, riêng tư, độ trễ ổn định, có SLA, đơn giản; thêm IPsec để mã hóa | Giá cao hơn băng rộng; một nhà mạng một điểm hỏng nếu không có đường dự phòng |
| MPLS L3VPN | Cao nhất (khoảng 1,5 lần DIA cùng băng thông) | QoS và SLA tích hợp, định tuyến do nhà mạng quản lý | Phụ thuộc nhà mạng, khó đổi nhà mạng, khó mở rộng lên đám mây |
| SD-WAN trên đường DIA | Thấp hơn MPLS khoảng 25% | Chọn đường theo ứng dụng, quản lý tập trung | Chất lượng phụ thuộc đường nền, cần thiết bị và giấy phép từng site |
| SD-WAN trên băng rộng | Thấp nhất, tiết kiệm đến khoảng 70% so với MPLS | Rẻ, triển khai nhanh | Không có SLA, độ trễ và mất gói biến động, không hợp cho HIS và PACS làm đường chính |
| IPsec thẳng trên Internet | Thấp (chỉ phí đường Internet sẵn có) | Rẻ, không cần thuê thêm | Không SLA, chia sẻ đường với lưu lượng Internet |
| VPLS hoặc Metro Ethernet | Cao, tương tự kênh thuê riêng | Hai chi nhánh cùng một mạng L2 | Miền broadcast rộng, thường không có tại mọi địa chỉ |

Phương án chọn: kênh thuê riêng L2 đối xứng 500 Mbps mỗi chi nhánh, mã hóa bằng IPsec, về sau thêm đường băng rộng giá rẻ làm dự phòng bằng SD-WAN (hướng phát triển). Lý do: HIS và PACS nhạy với độ trễ và mất gói, đường riêng cho chất lượng dự đoán được; mã hóa IPsec bù phần bảo mật mà L2 thuần không có. Nhược điểm cần chấp nhận là chi phí cao hơn và không có đường dự phòng ngay từ đầu; chi nhánh mất kết nối vẫn dùng được dịch vụ cục bộ nhờ hai server riêng.
