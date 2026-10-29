# Nghiên cứu 02 - Công nghệ lõi (Step 3, 4, 5, 6)

Mục đích: hiểu vì sao chọn, cần kiểm tra bằng lệnh nào, và bẫy thường gặp. Phần cấu hình tự viết; ở đây chỉ ghi khung lệnh để biết cần tìm gì.

## 1. Spanning Tree và Layer 2 (Step 3)

Lựa chọn:
- Rapid PVST+: của Cisco, một instance cho mỗi VLAN, cho phép cân bằng tải theo VLAN. Khuyến nghị cho môi trường toàn Cisco. Nhược điểm: tốn CPU khi số VLAN lớn.
- MSTP (802.1s): chuẩn mở, gộp nhiều VLAN vào ít instance (tối đa 64 mỗi region), hợp môi trường nhiều hãng hoặc rất nhiều VLAN.
- Với TVI (lab toàn Cisco, vài VLAN) thì Rapid PVST+ đơn giản hơn. Rationale cho báo cáo: phải nêu lý do này, và nhắc rằng MSTP là phương án khi mở rộng nhiều hãng.

Thực hành tốt:
- Đặt root bridge tường minh: priority 8192 cho core chính, 16384 cho core phụ (không để mặc định 32768). Lệnh `root primary/secondary` cũng được đề dùng.
- PortFast + BPDU Guard trên port access; Root Guard trên port hướng về switch không được làm root; Loop Guard cho link quang.
- Port không dùng: đưa vào VLAN 999 blackhole và shutdown (đề yêu cầu).

Kiểm tra: show spanning-tree, show spanning-tree vlan X detail, show spanning-tree bridge, show spanning-tree inconsistentports.

LACP: đề yêu cầu mode active (channel-group X mode active), không dùng PAgP/static. Kiểm tra: show etherchannel summary. Lưu ý: cần thử xem image switch trong lab hỗ trợ LACP không.

Bẫy: IOSvL2/IOL-L2 không dùng được VLAN 1002-1005 và không tagged VLAN 1 trên trunk; tránh các ID này khi quy hoạch VLAN.

## 2. First Hop Redundancy (Step 4)

HSRP:
- Host dùng virtual IP làm default gateway; router priority cao nhất là Active (mặc định 100). Đề yêu cầu priority 110 và preempt cho node primary.
- Lệnh chính: standby version 2, standby <group> ip, priority, preempt, track.
- Tracking: giảm priority khi uplink hỏng, nếu không Active vẫn nhận traffic và đẩy vào đường chết. Quan trọng cho kịch bản failover trong demo.
- Cân bằng tải: DSW1 Active cho VLAN 10, DSW2 Active cho VLAN 20, cân khớp với root bridge STP của cùng VLAN (căn chỉnh root bridge với HSRP active để traffic không đi vòng).
- Kiểm tra: show standby brief, show standby.

VRRP: chuẩn mở thay thế; IOSv không hỗ trợ VRRPv3 trên BVI. HSRP là lựa chọn an toàn cho lab Cisco.

DHCP tập trung + relay: ip helper-address trên SVI chi nhánh trỏ về server DHCP ở HQ; server cần pool theo từng subnet. Cần định tuyến đã chạy trước (Step 5) mới test được xuyên site, nên trong Week 2 chỉ test được relay giữa các VLAN trong cùng site.

## 3. OSPF (Step 5)

Thực hành tốt (Cisco TAC community):
- Đặt router-id tường minh; dùng Loopback0 và đưa vào OSPF.
- Link point-to-point giữa hai router nên đặt network type point-to-point để bỏ bầu DR/BDR.
- passive-interface default rồi chỉ mở interface cần adjacency; VLAN user luôn passive (đề yêu cầu).
- Dùng multi-area nếu cần summarization, mỗi area dùng khối địa chỉ liền kề; tốt nhất 2-4 ABR mỗi area.
- Summarize ở ABR/ASBR và thêm route null0 cho dải summary để tránh loop.

OSPFv3 cho IPv6: tương tự nhưng bật theo interface. Cần kiểm tra OSPFv3 có chạy trên image switch lab không (nguồn tôi đọc không xác nhận).

Kiểm tra: show ip ospf neighbor, show ip route ospf, show ip ospf interface brief, ping loopback.

Thiết kế gợi ý để cân nhắc: mỗi site là một area, area 0 là backbone nối các site? Hoặc OSPF chỉ chạy trong từng site (đúng với đề: "OSPF cho định tuyến nội bộ từng site", BGP cho liên site). Theo đề thì mỗi site là một OSPF domain độc lập, BGP nối các site.

## 4. BGP và WAN edge (Step 6)

- eBGP với ISP; iBGP trong AS của TVI giữa các edge router; next-hop-self trên iBGP khi đi qua eBGP.
- Summarization tại chi nhánh bằng aggregate-address để giảm bảng định tuyến (rubric Step 6 và checklist đều nhắc).
- Chọn thiết kế AS: một AS riêng cho TVI (AS private), ISP một hoặc hai AS; dual-ISP (đề nói broadband + MPLS underlay) cần xử lý local-preference/MED để chọn đường chính.

IPsec site-to-site (VTI, route-based) trên IOS XE:
1. IKEv2 proposal (ví dụ AES-GCM-256, DH 19/20), policy, keyring (PSK), profile.
2. IPsec transform set (ESP, tunnel mode) và IPsec profile gắn với IKEv2 profile.
3. Interface Tunnel: tunnel mode ipsec ipv4, tunnel source/destination, tunnel protection ipsec profile.
4. Chạy BGP (hoặc OSPF) qua tunnel như qua link thường.
Lưu ý từ tài liệu Cisco: IOS XE không chạy nhiều VTI cùng source và destination nên dùng loopback làm source cho tunnel khi cần nhiều tunnel; BGP qua tunnel có thể cần ebgp-multihop.
Kiểm tra: show crypto ikev2 sa, show crypto ipsec sa (counter encaps/decaps tăng), show ip bgp summary, show ip route.
Chưa xác nhận: cú pháp IKEv2 có chạy trên IOSv/IOL không (nguồn tôi đọc dùng Cat8000v). Cần test; nếu không, dùng IKEv1/crypto map kiểu cũ hoặc GRE over IPsec.

## 5. EVPN-VXLAN (phần tùy chọn)

- Khái niệm: underlay IP (OSPF/BGP) + overlay VXLAN, control plane MP-BGP EVPN; VTEP, VNI, MAC-VRF (l2vpn evpn instance), NVE interface.
- Nền tảng chạy được theo nguồn: IOL (L3) và IOL-L2 cho kịch bản L2, Catalyst 8000v (cần Premier license). CSR1000v không hỗ trợ EVPN với VXLAN. IOSv không có tài liệu.
- Giới hạn lab đã ghi nhận: VNI từ 4096 trở lên; VLAN interface IOL-L2 có thể cần tắt autostate; eBGP EVPN với next hop loopback cần ebgp-multihop và route-map đặt next-hop unchanged.
- Đề không bắt buộc EVPN ở Step 6 ("iBGP/EVPN hoặc IPsec"), nhưng phần Data Center Fabric (spine-leaf, EVPN-VXLAN) được liệt kê trong features, nên báo cáo nên giải thích thiết kế DC fabric dù lab dùng IPsec.
