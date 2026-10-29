# Assignment 2 - Giải thích đề (TVI Enterprise Network)

Nguồn: Assignment 2 - Large Enterprise Network Design and Implementation.docx

## 1. Đề bài thực chất yêu cầu gì

Đóng vai Lead Network Architect cho công ty giả định TechViet Innovations (TVI). Công ty đang dùng mạng cũ (flat, hub-and-spoke, routing động lỗi thời, bảo mật theo vành đai) và cần được thiết kế lại. Nhiệm vụ gồm 3 phần gắn chặt với nhau:

1. Thiết kế: vẽ topology, quy hoạch IP (IPv4 VLSM + IPv6 phân cấp), chọn công nghệ và giải thích vì sao chọn.
2. Hiện thực trong lab ảo: dựng topology trên EVE-NG / GNS3 / CML, cấu hình thật các giao thức và chứng minh chạy được.
3. Báo cáo + demo: Technical Explanation Report (PDF), file cấu hình, script automation, và demo trực tiếp 15 phút.

Điểm mấu chốt: không chỉ cấu hình cho chạy, mà phải giải thích được lý do thiết kế (rubric dành 20% cho phần rationale) và có bằng chứng kiểm thử (15%).

## 2. Ba site cần thiết kế

| Site | Vai trò | Quy mô | Đặc thù |
|---|---|---|---|
| HCMC (HQ) | Data center, văn phòng điều hành | 2,000+ user | Backbone 10/40 Gbps, DHCP/DNS tập trung, Executive và Finance cần bảo mật cao nhất |
| Hanoi | R&D, AI lab | 1,500+ user | Băng thông east-west lớn cho training AI |
| Da Nang | Logistics, kho | 500+ user, nhiều IoT | Wi-Fi 6/7 độ trễ thấp cho AGV và máy quét |

Tổng: 4,000+ user nội bộ, 10,000+ thiết bị IoT, mạng guest, mở rộng tới 10,000+ user năm 2030. Uptime 99.99%.

Các nhóm người dùng cần phân tách bằng VLAN và chính sách riêng: Executives/Finance, R&D Engineers, Logistics, Remote workforce (ZTNA/SASE), Guests (chỉ internet).

## 3. Bốn nhu cầu cốt lõi và công nghệ đáp ứng

| Nhu cầu | Ý nghĩa | Công nghệ trả lời |
|---|---|---|
| High availability | Không có single point of failure ở L2 và L3 | EtherChannel LACP, Rapid PVST+/MSTP, HSRP/VRRP, dual-ISP |
| Secure remote access | Bỏ VPN cũ, chuyển sang Zero Trust | ZTNA/SASE (chủ yếu trình bày trong báo cáo, không bắt buộc mô phỏng) |
| Optimized traffic | Chi nhánh ra cloud trực tiếp, không backhaul về HQ | SD-WAN concept, local internet breakout, NAT/PAT tại edge |
| Agility/automation | Tạo VLAN, policy bằng code | Python Netmiko/NAPALM hoặc Ansible |

## 4. Giao thức trong đề và vai trò của từng cái (hiểu nhanh)

- OSPF (OSPFv3 cho IPv6): underlay, định tuyến nội bộ từng site, mọi Loopback0 phải reach được.
- BGP: overlay/WAN, eBGP với ISP, iBGP giữa các site, summarization ở chi nhánh.
- EVPN-VXLAN: data center fabric spine-leaf, L2 over L3. Đề liệt kê trong feature nhưng Step 6 chỉ ghi "iBGP/EVPN hoặc IPsec", nghĩa là chọn một.
- IPsec VPN: tunnel site-to-site HQ với Hanoi và Da Nang.
- NAT/PAT: ra internet tại edge router.
- HSRP/VRRP: gateway ảo dự phòng, primary priority 110 có preempt.
- LACP: gộp link giữa các switch core/distribution.
- STP (Rapid PVST+/MSTP): chống loop, ép root bridge thủ công.
- DHCP tập trung tại HQ + DHCP relay (ip helper-address) ở chi nhánh.
- Layer 2 security: Port Security, DHCP Snooping, Dynamic ARP Inspection.
- QoS: VoIP đánh dấu EF, video AF31, ưu tiên trên WAN.
- ACL / zone-based firewall: tách Guest, IoT, Corporate.
- CAPWAP/WLC: tích hợp wireless (trình bày, khó mô phỏng trên vIOS).

## 5. 10 bước chấm điểm (mỗi bước 1.0, tổng 10)

| Bước | Nội dung | Kết quả cần nộp |
|---|---|---|
| 1 | Phân tích yêu cầu, logical topology | Diagram Visio/Draw.io: HQ, branches, ISP, demarcation point |
| 2 | IP addressing | Excel/Markdown: VLSM IPv4 + IPv6 phân cấp cho mọi site |
| 3 | Layer 2 | VLAN, trunk 802.1Q, EtherChannel, RSTP/MSTP, root bridge |
| 4 | FHRP và IP services | HSRP/VRRP, DHCP/DNS tập trung chạy xuyên router |
| 5 | Underlay IGP | OSPF hội tụ từng site, loopback reach được |
| 6 | BGP và WAN edge | eBGP với ISP, iBGP/EVPN hoặc IPsec nối HQ-Hanoi-Da Nang |
| 7 | Security | ACL Guest/Corp, NAT overload, DHCP Snooping/DAI |
| 8 | QoS | Marking và ưu tiên VoIP trên WAN |
| 9 | Automation | Python hoặc Ansible: tạo VLAN, backup config |
| 10 | Test và tài liệu | Ping/trace end-to-end, báo cáo, tài liệu vận hành |

## 6. Step 9 (automation) chi tiết

Ba việc bắt buộc:

1. Inventory ngoài code (inventory.yaml hoặc Ansible hosts); credential qua env var, getpass hoặc Ansible Vault; cấm password plaintext.
2. Đẩy baseline (AAA, NTP, Syslog, banner) và tạo VLAN 10 Executive, 20 Engineering, 30 Logistics, 99 Management.
3. Chụp show running-config và show ip interface brief trước và sau khi đổi; lưu file timestamp vào backups/; ghi log thành công và lỗi SSH vào logs/automation.log.

Tiêu chí chấm Step 9: chạy thành công 50%, xử lý lỗi và idempotency 30%, chất lượng code và bảo mật 20%. Đề có kèm starter code mẫu (Netmiko và Ansible); cần hiểu và viết lại theo phong cách riêng, vì phần oral defense yêu cầu giải thích 100% code.

## 7. Báo cáo (PDF) - rubric

| Tiêu chí | Trọng số |
|---|---|
| Executive summary gắn business | 10% |
| Diagram kiến trúc/topology | 15% |
| IP schema IPv4/IPv6 | 15% |
| Rationale công nghệ lõi (OSPF, BGP, EVPN, STP, HSRP) | 20% |
| Security, QoS, automation | 15% |
| Testing, verification, failover | 15% |
| Format, rõ ràng, chuyên nghiệp | 10% |

Báo cáo phải có mục lục, số trang, một file PDF; văn xuôi AI chưa biên tập sẽ bị trừ điểm.

## 8. Demo

15 phút live: connectivity end-to-end, failover (shutdown core link, hội tụ dưới 3 phút), chạy automation script. Nếu báo cáo nói failover thành công mà demo không tái hiện được thì bị trừ điểm verification.

## 9. Quy tắc liêm chính

- Push code liên tục lên GitHub/GitLab (commit log là bằng chứng đóng góp).
- AI chỉ để tra cú pháp và debug; phải giải thích được 100% code khi bảo vệ, không giải thích được thì 0 điểm phần đó.
- Đạo văn giữa các nhóm hoặc chép repo ngoài không ghi nguồn: 0 điểm toàn nhóm. Đặt tên thiết bị trùng nhóm khác cũng bị xem xét.

## 10. Điểm mâu thuẫn / chưa rõ trong đề (cần hỏi giảng viên)

1. Thời gian: đề ghi 6 tuần nhưng phần Academic Integrity ghi 8 tuần.
2. Deadline: đề ghi "Sunday, November 17, 2026" nhưng 17/11/2026 là thứ Ba. Cần xác nhận ngày chính xác.
3. Mục "Required Submission Content" nói về client/server scripts và sequence diagram, giống hệt Assignment 1 (có vẻ copy nhầm). Cấu trúc nộp đúng của Assignment 2 có vẻ là cây thư mục Report / Configurations / Automation trong checklist.
4. Làm nhóm hay cá nhân: đề ghi "Group/Individual".
5. Thang điểm: tổng 10 điểm nhưng ghi chú trừ "up to 10 points" ở rubric báo cáo; cần hỏi cách quy đổi.
6. EVPN-VXLAN: image vIOS/vIOS-L2 thường không hỗ trợ VXLAN/EVPN. Nếu muốn làm thật cần vEOS/Nexus hoặc chấp nhận làm IPsec cho Step 6 và trình bày EVPN ở mức thiết kế. Cần xác nhận với giảng viên.
7. Cisco image: vIOS/vIOS-L2 lấy từ đâu (đề không cung cấp, cần license/CML hoặc nguồn của trường).
