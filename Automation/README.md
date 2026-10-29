# Automation

Script Netmiko đẩy cấu hình từ thư mục Configurations/ lên thiết bị. Chạy lại nhiều lần không làm hỏng cấu hình: script đọc running-config, chỉ gửi những dòng còn thiếu, rồi đọc lại để kiểm tra.

## Cài đặt (Windows, macOS, Linux)

```
python -m venv .venv
.venv\Scripts\activate          (Windows)
source .venv/bin/activate       (macOS, Linux)
pip install -r requirements.txt
```

Tài khoản đặt bằng biến môi trường, không ghi vào repo: TVI_USER, TVI_PASS, TVI_ENABLE (nếu bỏ trống thì dùng TVI_PASS).

## Dùng

```
python deploy.py backup
python deploy.py plan --site HCM
python deploy.py apply --device HCM-R1 --part 02 --save
```

- backup: lưu running-config vào Automation/backups/
- plan: chỉ in các lệnh sẽ gửi, không thay đổi thiết bị
- apply: gửi lệnh còn thiếu, đọc lại để kiểm tra, trả mã thoát khác 0 nếu còn dòng thiếu
- --device, --site, --part lọc thiết bị, site và nhóm file (02 là file bắt đầu bằng 02)
- --save lưu startup-config sau khi apply thành công

## Quy ước

- Cấu hình nằm ở Configurations/<tên thiết bị>/NN-<nhóm>.cfg, file được áp dụng theo thứ tự tên: 01 là Layer 2 và gateway, 02 là định tuyến và WAN, 03 là bảo mật và QoS.
- Địa chỉ quản trị mỗi thiết bị khai trong inventory.yml. Phải sửa cho khớp lab thật (EVE-NG hoặc GNS3) trước khi chạy.
- ISP không nằm trong inventory vì không thuộc mạng TVI; cấu hình của ISP ở Configurations/ISP/ nạp bằng tay.
- Tên cổng (GigabitEthernet0/0...) là giả định cho IOS router và switch L3; đổi theo image thật nếu khác.

## Kiểm tra

```
python -m unittest
python check_plan.py
```

check_plan.py kiểm tra ip-plan.yml: subnet không trùng, gateway nằm trong subnet, IPv6 đúng /64 trong /48 của site, đủ chỗ cho số người.
