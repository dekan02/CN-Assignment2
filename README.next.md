# Assignment 2 - Thiết kế mạng cho bệnh viện chuyên khoa

Bài tập lớn môn Mạng máy tính (HK261). Thiết kế mạng cho một bệnh viện chuyên khoa gồm trụ sở TP.HCM (hai tòa A và B, 600 máy trạm, 10 server) và hai chi nhánh (DBP, BHTQ, mỗi nơi 260 máy trạm, 2 server), mô phỏng bằng Packet Tracer.

## Cấu trúc thư mục

| Đường dẫn | Nội dung |
|---|---|
| `docs/01_nghien-cuu.md` | Nghiên cứu và nguồn tham khảo |
| `docs/02_phan-tich-yeu-cau.md` | Bước 1: phân tích cấu trúc, checklist khảo sát, khu vực tải cao, WiFi, DMZ và firewall |
| `docs/03_thiet-ke-chi-tiet.md` | Bước 2: danh sách thiết bị, IP plan, sơ đồ cáp, sơ đồ WAN, định tuyến |
| `docs/04_luu-luong-bang-thong.md` | Bước 3: tính lưu lượng và băng thông, chọn đường Internet và WAN |
| `docs/05_huong-dan-packet-tracer.md` | Bước 4 và 5: dựng mô phỏng, kiểm thử bằng ping và traceroute |
| `docs/06_danh-gia.md` | Bước 6: đánh giá, vấn đề còn lại, hướng phát triển, phần mở rộng bảo mật |
| `docs/07_ly-do-thiet-ke.md` | Lý do của từng quyết định thiết kế, phương án đã cân nhắc, đánh đổi |
| `docs/images/` | Ảnh sơ đồ logic, vật lý, WAN (PNG) |
| `docs/generated/` | Bảng IP, liên kết, đấu nối, băng thông, số lượng thiết bị (sinh tự động) |
| `Configurations/` | Cấu hình IOS và ASA cho từng thiết bị trong mô phỏng (sinh tự động) |
| `tools/` | Mô hình dữ liệu và bộ sinh tài liệu, cấu hình |
| `Simulation/` | File `.pkt` |
| `Report/` | Báo cáo nộp |

## Sinh lại tài liệu và cấu hình

Yêu cầu Python 3, không cần thư viện ngoài.

```
python3 tools/design.py
```

Lệnh này kiểm tra mô hình (không trùng VLAN và subnet, đủ chỗ cho số host, tổng máy trạm khớp 600 và 260), rồi ghi lại `docs/generated/` và `Configurations/`. Muốn đổi địa chỉ hoặc số máy, sửa `tools/model.py` hoặc `tools/topology.py` rồi chạy lại; không sửa tay các file được sinh.

## Phân công và tiến độ

| Việc | Trạng thái |
|---|---|
| Nghiên cứu | Xong |
| Bước 1: phân tích yêu cầu | Bản nháp |
| Bước 2: thiết kế chi tiết, IP plan, sơ đồ | Bản nháp |
| Bước 3: lưu lượng và băng thông | Bản nháp, thiếu báo giá nhà mạng |
| Bước 4: dựng mô phỏng Packet Tracer | Chưa làm |
| Bước 5: kiểm thử ping, traceroute | Chưa làm |
| Bước 6: đánh giá | Bản nháp |
| Bước 7: báo cáo và nộp BKeL | Chưa làm |
| Kiểm chứng các tính năng chưa chắc trong Packet Tracer | Chưa làm |

## Quy ước

- Nhánh `develop` là nhánh làm việc chung; mỗi việc một nhánh con, gộp vào `develop` khi xong.
- Tài liệu viết bằng tiếng Việt, giữ thuật ngữ kỹ thuật tiếng Anh.
- Mã nguồn không có chú thích.
- Mật khẩu trong `Configurations/` chỉ là giá trị dùng cho bài lab.
