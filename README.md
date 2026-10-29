# TVI Large Enterprise Network (Assignment 2)

Môn Computer Network HK261. Thiết kế và dựng mạng cho TechViet Innovations gồm 3 site: TP.HCM (HQ), Hà Nội (R&D), Đà Nẵng (kho vận, nhiều IoT). Đề yêu cầu 10 bước kỹ thuật, báo cáo PDF, file cấu hình, script tự động hóa và demo 15 phút (failover lõi dưới 3 phút).

Đây là repo làm việc của nhóm 2 người. Tài liệu gốc về đề nằm trong docs/.

## Bắt đầu đọc từ đâu

1. docs/05_topology.html (mở bằng trình duyệt): sơ đồ topology, bảng VLAN và IP, công nghệ chạy ở thiết bị nào.
2. docs/06_phan-viec-chia-nhom.md: ai làm phần nào.
3. docs/01_assignment-explained.md: giải thích đề chi tiết.

## Phân việc

| Nhóm | Nội dung | Người làm | Trạng thái |
|---|---|---|---|
| 1 | Layer 2 (VLAN, trunk, LACP, STP), HSRP, DHCP relay | Đồng đội | Chưa làm |
| 2 | OSPF, BGP, IPsec | Khang | Đã viết cấu hình, chưa thử trên lab thật |
| 3 | NAT, ACL, DHCP Snooping, DAI, QoS | Đồng đội | Chưa làm |
| 4 | Script Netmiko, kế hoạch IP | Khang | Đã viết, chưa thử trên lab thật |
| 5 | Báo cáo PDF, đóng gói ZIP | Cả hai | Chưa làm |

## Cấu trúc thư mục

- docs/: giải thích đề, kế hoạch, thiết kế topology, phân việc, lệnh kiểm tra
- research/: nghiên cứu công nghệ và nền tảng lab, có nguồn
- Configurations/: cấu hình từng thiết bị
- Automation/: script Netmiko, inventory, kế hoạch IP, script kiểm tra IP
- lab-frr/: lab luyện tập BGP và OSPF bằng FRR (chỉ để thử trên Mac, không nằm trong bài nộp)
- Report/: báo cáo PDF

## Quy ước cấu hình (quan trọng khi thêm phần của mình)

Mỗi thiết bị có thư mục riêng, Configurations/<tên thiết bị>/. Mỗi nhóm viết một file riêng trong đó, đặt tên theo số thứ tự:

- 01-<tên>.cfg: Layer 2, VLAN, HSRP, DHCP relay (nhóm 1)
- 02-routing.cfg: OSPF, BGP, IPsec (nhóm 2, đã có)
- 03-<tên>.cfg: NAT, ACL, Snooping, DAI, QoS (nhóm 3)

Script deploy áp dụng các file theo thứ tự tên, nên mỗi người chỉ sửa file của mình và không xung đột khi merge. Dùng đúng tên thiết bị trong sơ đồ (HCM-R1, HCM-CORE1, HCM-CORE2, HCM-ACC1, HN-R1, HN-SW1, HN-ACC1, DN-R1, DN-SW1) và đúng địa chỉ trong docs/05_topology-design.md hoặc Automation/ip-plan.yml. File cấu hình viết theo kiểu running-config của Cisco IOS, thụt lề một khoảng trắng cho lệnh con.

Nếu cần thêm hoặc đổi địa chỉ, sửa Automation/ip-plan.yml rồi chạy python Automation/check_plan.py để chắc không trùng dải.

## Những điểm cần biết

- Mô hình giữa các site là hub and spoke: HN và DN nói chuyện với nhau qua HCM-R1. ISP chỉ gửi lại route mặc định và nhận khối địa chỉ công cộng của mỗi site, nên mọi lưu lượng giữa các site phải đi qua tunnel IPsec.
- Cổng nối giữa các thiết bị giả định là GigabitEthernet0/0, 0/1, 0/2 như docs/05_topology-design.md. Nếu image trong lab dùng tên khác thì đổi trong file cấu hình.
- Tên cổng, IP quản trị trong Automation/inventory.yml và khóa IPsec thử nghiệm trong 02-routing.cfg chưa được kiểm chứng trên lab thật. Cần chỉnh khi dựng lab.
- Chưa chốt nền tảng lab thật (EVE-NG hoặc GNS3 trên máy x86 của một thành viên) và nguồn image Cisco hợp pháp. Image Cisco lấy từ CML không được dùng ngoài CML theo giấy phép.
- lab-frr/ dùng FRR nên cú pháp khác Cisco IOS và dải địa chỉ cũ. Chỉ dùng để luyện, không đưa vào bài nộp.
- EVPN-VXLAN chưa làm trong lab; dự kiến chỉ trình bày ở mức thiết kế trong báo cáo.

## Chạy và kiểm tra

Kiểm tra kế hoạch IP và script, chạy trên mọi hệ điều hành có Python:

```
pip install -r Automation/requirements.txt
python Automation/check_plan.py
cd Automation
python -m unittest
```

Đẩy cấu hình lên thiết bị (sau khi lab chạy và inventory đã đúng), xem Automation/README.md:

```
python deploy.py plan --site HCM
python deploy.py apply --site HCM --save
```

Lệnh kiểm tra OSPF, BGP, IPsec sau khi nạp cấu hình: docs/07_routing-verification.md.

Lab FRR trên Mac (cần Docker Desktop):

```
cd lab-frr
bash run.sh
```

## Quy trình git

- main: bản ổn định. develop: nơi gộp công việc của cả hai.
- Mỗi người làm trên branch riêng, ví dụ khang/routing-automation, rồi merge vào develop.
- Commit nhỏ, đúng tài khoản của mình; lịch sử commit là bằng chứng đóng góp của từng người.
- Không commit file log, thư mục clab-tvi, thư mục backups, mật khẩu thật.

## Hạn nộp

Đề ghi 17/11/2026 nhưng đang mâu thuẫn (ghi là Chủ nhật, thực tế là thứ Ba). Cần hỏi giảng viên cùng các câu về EVPN, nguồn image và quy mô nhóm.
