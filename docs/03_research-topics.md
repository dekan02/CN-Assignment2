# Assignment 2 - Danh sách cần nghiên cứu

Mỗi mục: cần hiểu gì, để dùng ở bước nào. Tick khi đã nắm đủ để giải thích bằng lời riêng.

## Thiết kế và địa chỉ (Step 1-2)
- [ ] Mô hình mạng enterprise: three-tier vs collapsed core, demarcation point, trust zone. 
- [ ] VLSM: cách chia subnet theo số host từng VLAN, chừa chỗ tăng trưởng tới 2030.
- [ ] IPv6 phân cấp: prefix /48 cho site, /64 cho VLAN, dual-stack.
- [ ] Route summarization: thiết kế block liền kề cho từng site.

## Layer 2 (Step 3)
- [ ] 802.1Q trunking, native VLAN, VLAN 999 blackhole cho port không dùng.
- [ ] LACP (channel-group mode active) so với PAgP/static.
- [ ] Rapid PVST+ so với MSTP; cách ép root bridge primary/secondary.

## FHRP và dịch vụ IP (Step 4)
- [ ] HSRP vs VRRP: virtual IP, priority, preempt, track.
- [ ] DHCP relay (ip helper-address), DHCP server tập trung nhiều scope.
- [ ] DNS nội bộ cơ bản.

## Routing (Step 5-6)
- [ ] OSPF single/multi-area, passive-interface, router-id, loopback; OSPFv3.
- [ ] BGP: eBGP vs iBGP, next-hop-self, network/aggregate-address, route filtering cơ bản.
- [ ] Underlay vs overlay, và vì sao tách hai tầng.
- [ ] IPsec site-to-site (IKEv2/ISAKMP, transform set, crypto map hoặc VTI); GRE over IPsec.
- [ ] EVPN-VXLAN: khái niệm VTEP, VNI, MP-BGP EVPN, spine-leaf (để giải thích trong báo cáo; kiểm tra image nào hỗ trợ).
- [ ] SD-WAN concept, local internet breakout.

## Security (Step 7)
- [ ] ACL extended, vị trí đặt ACL, thứ tự rule, cách tách Guest/IoT/Corp.
- [ ] NAT/PAT overload.
- [ ] DHCP Snooping, DAI, Port Security: cách hoạt động và trusted port.
- [ ] Hardening: SSHv2, bỏ Telnet/HTTP/SNMPv1-2c, SNMPv3.
- [ ] ZTNA/SASE, micro-segmentation, zone-based firewall (khái niệm cho báo cáo).

## QoS (Step 8)
- [ ] DSCP/CoS, EF và AF31, class-map/policy-map/service-policy, LLQ.
- [ ] Cách tạo traffic VoIP giả để kiểm chứng (ví dụ ping với ToS, IP SLA).

## Wireless (khái niệm)
- [ ] WLC, CAPWAP, Wi-Fi 6/7 cho AGV: trình bày ở mức thiết kế.

## Automation (Step 9)
- [ ] Python: netmiko ConnectHandler, send_command, send_config_set, xử lý NetmikoTimeoutException và NetmikoAuthenticationException, yaml.safe_load, logging, getpass.
- [ ] Ansible: inventory, network_cli, cisco.ios modules, Vault, idempotency.
- [ ] Lập luận idempotency: kiểm tra trạng thái trước khi đổi.

## Lab và công cụ
- [ ] EVE-NG / GNS3 / CML: cài, upload image, fixpermissions, quản lý RAM.
- [ ] Phương án chạy trên MacBook ARM (xem file 02).
- [ ] Draw.io cho diagram, Excel cho IP plan, git workflow.

## Báo cáo
- [ ] Cấu trúc báo cáo theo rubric (file 01 mục 7), viết bằng văn phong kỹ thuật tự biên tập, có trích nguồn.
