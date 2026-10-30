# Bảng đấu nối

| # | Thiết bị 1 | Cổng | Thiết bị 2 | Cổng | Loại cáp |
|---|---|---|---|---|---|
| 1 | ISP1 | Gi0/0 | EDGE1 | Gi0/0 | Đồng thẳng |
| 2 | ISP1 | Gi0/1 | INET | Gi0/0 | Đồng thẳng |
| 3 | ISP2 | Gi0/0 | EDGE2 | Gi0/0 | Đồng thẳng |
| 4 | ISP2 | Gi0/1 | INET | Gi0/1 | Đồng thẳng |
| 5 | ISP2 | Gi0/2 | TELE-PC | Fa0 | Đồng chéo |
| 6 | INET | Gi0/2 | WEB-INET | Fa0 | Đồng chéo |
| 7 | EDGE1 | Gi0/1 | FW-HCM | Gi1/1 | Đồng chéo |
| 8 | EDGE2 | Gi0/1 | FW-HCM | Gi1/2 | Đồng chéo |
| 9 | FW-HCM | Gi1/3 | CORE1 | Gi1/0/1 | Đồng chéo |
| 10 | FW-HCM | Gi1/4 | SW-DMZ | Gi0/1 | Đồng thẳng |
| 11 | FW-HCM | Gi1/5 | SW-SRV | Gi0/1 | Đồng thẳng |
| 12 | SW-DMZ | Fa0/1 | PORTAL | Fa0 | Đồng thẳng |
| 13 | SW-DMZ | Fa0/2 | MAIL-GW | Fa0 | Đồng thẳng |
| 14 | SW-SRV | Fa0/1 | HIS-APP | Fa0 | Đồng thẳng |
| 15 | SW-SRV | Fa0/2 | PACS | Fa0 | Đồng thẳng |
| 16 | SW-SRV | Fa0/3 | AD-DNS | Fa0 | Đồng thẳng |
| 17 | SW-SRV | Fa0/4 | NMS | Fa0 | Đồng thẳng |
| 18 | SW-SRV | Fa0/5 | NVR | Fa0 | Đồng thẳng |
| 19 | CORE1 | Gi1/0/2 | CORE2 | Gi1/0/2 | Đồng chéo |
| 20 | CORE1 | Gi1/0/3 | DS-A1 | Gi1/0/1 | Đồng chéo |
| 21 | CORE2 | Gi1/0/3 | DS-A1 | Gi1/0/2 | Đồng chéo |
| 22 | CORE1 | Gi1/0/4 | DS-A2 | Gi1/0/1 | Đồng chéo |
| 23 | CORE2 | Gi1/0/4 | DS-A2 | Gi1/0/2 | Đồng chéo |
| 24 | CORE1 | Gi1/0/5 | DS-B1 | Gi1/0/1 | Đồng chéo |
| 25 | CORE2 | Gi1/0/5 | DS-B1 | Gi1/0/2 | Đồng chéo |
| 26 | CORE1 | Gi1/0/6 | DS-B2 | Gi1/0/1 | Đồng chéo |
| 27 | CORE2 | Gi1/0/6 | DS-B2 | Gi1/0/2 | Đồng chéo |
| 28 | CORE1 | Gi1/0/7 | R-WAN1 | Gi0/0 | Đồng chéo |
| 29 | CORE2 | Gi1/0/7 | R-WAN2 | Gi0/0 | Đồng chéo |
| 30 | CORE1 | Gi1/0/8 | WLC | Port 1 | Đồng thẳng |
| 31 | R-WAN1 | Gi0/1 | R-DBP | Gi0/0 | Đồng chéo |
| 32 | R-WAN2 | Gi0/1 | R-BHTQ | Gi0/0 | Đồng chéo |
| 33 | DS-A1 | Gi1/0/3 | ACC-A | Gi0/1 | Đồng chéo |
| 34 | DS-A2 | Gi1/0/3 | ACC-A | Gi0/2 | Đồng chéo |
| 35 | DS-A1 | Gi1/0/4 | DS-A2 | Gi1/0/4 | Đồng chéo |
| 36 | DS-B1 | Gi1/0/3 | ACC-B | Gi0/1 | Đồng chéo |
| 37 | DS-B2 | Gi1/0/3 | ACC-B | Gi0/2 | Đồng chéo |
| 38 | DS-B1 | Gi1/0/4 | DS-B2 | Gi1/0/4 | Đồng chéo |
| 39 | ACC-A | Fa0/1 | PC-A-RECEPTION | Fa0 | Đồng thẳng |
| 40 | ACC-A | Fa0/2 | PC-A-PHARMACY | Fa0 | Đồng thẳng |
| 41 | ACC-A | Fa0/3 | PC-A-OUTPATIENT-1 | Fa0 | Đồng thẳng |
| 42 | ACC-A | Fa0/4 | PC-A-LAB | Fa0 | Đồng thẳng |
| 43 | ACC-A | Fa0/5 | PC-A-IMAGING | Fa0 | Đồng thẳng |
| 44 | ACC-A | Fa0/6 | PC-A-SURGERY | Fa0 | Đồng thẳng |
| 45 | ACC-A | Fa0/7 | AP-A | Port 0 | Đồng thẳng |
| 46 | ACC-A | Fa0/8 | CAM-A | Fa0 | Đồng thẳng |
| 47 | ACC-A | Fa0/9 | MED-A | Fa0 | Đồng thẳng |
| 48 | ACC-A | Fa0/10 | PHONE-A | Fa0 | Đồng thẳng |
| 49 | ACC-A | Fa0/11 | PC-A-OUTPATIENT-2 | Fa0 | Đồng thẳng |
| 50 | ACC-B | Fa0/1 | PC-B-ER | Fa0 | Đồng thẳng |
| 51 | ACC-B | Fa0/2 | PC-B-INPATIENT-1 | Fa0 | Đồng thẳng |
| 52 | ACC-B | Fa0/3 | PC-B-ADMIN | Fa0 | Đồng thẳng |
| 53 | ACC-B | Fa0/4 | PC-B-FINANCE | Fa0 | Đồng thẳng |
| 54 | ACC-B | Fa0/5 | PC-B-TRAINING | Fa0 | Đồng thẳng |
| 55 | ACC-B | Fa0/6 | PC-B-IT | Fa0 | Đồng thẳng |
| 56 | ACC-B | Fa0/7 | AP-B | Port 0 | Đồng thẳng |
| 57 | ACC-B | Fa0/8 | CAM-B | Fa0 | Đồng thẳng |
| 58 | ACC-B | Fa0/9 | MED-B | Fa0 | Đồng thẳng |
| 59 | ACC-B | Fa0/10 | PHONE-B | Fa0 | Đồng thẳng |
| 60 | ACC-B | Fa0/11 | PC-B-INPATIENT-2 | Fa0 | Đồng thẳng |
| 61 | R-DBP | Gi0/1 | SW-DBP-1 | Gi0/1 | Đồng chéo |
| 62 | SW-DBP-1 | Gi0/2 | SW-DBP-2 | Gi0/1 | Đồng chéo |
| 63 | SW-DBP-1 | Fa0/1 | PC-DBP-CLINIC-1 | Fa0 | Đồng thẳng |
| 64 | SW-DBP-1 | Fa0/2 | PC-DBP-LABIMG | Fa0 | Đồng thẳng |
| 65 | SW-DBP-1 | Fa0/3 | AP-DBP-1 | Port 0 | Đồng thẳng |
| 66 | SW-DBP-1 | Fa0/4 | CAM-DBP | Fa0 | Đồng thẳng |
| 67 | SW-DBP-1 | Fa0/5 | PHONE-DBP | Fa0 | Đồng thẳng |
| 68 | SW-DBP-1 | Fa0/6 | PC-DBP-CLINIC-2 | Fa0 | Đồng thẳng |
| 69 | SW-DBP-2 | Fa0/1 | PC-DBP-ADMIN | Fa0 | Đồng thẳng |
| 70 | SW-DBP-2 | Fa0/2 | PC-DBP-IT | Fa0 | Đồng thẳng |
| 71 | SW-DBP-2 | Fa0/3 | MED-DBP | Fa0 | Đồng thẳng |
| 72 | SW-DBP-2 | Fa0/4 | SRV-DBP | Fa0 | Đồng thẳng |
| 73 | SW-DBP-2 | Fa0/5 | AP-DBP-2 | Port 0 | Đồng thẳng |
| 74 | R-BHTQ | Gi0/1 | SW-BHTQ-1 | Gi0/1 | Đồng chéo |
| 75 | SW-BHTQ-1 | Gi0/2 | SW-BHTQ-2 | Gi0/1 | Đồng chéo |
| 76 | SW-BHTQ-1 | Fa0/1 | PC-BHTQ-CLINIC-1 | Fa0 | Đồng thẳng |
| 77 | SW-BHTQ-1 | Fa0/2 | PC-BHTQ-LABIMG | Fa0 | Đồng thẳng |
| 78 | SW-BHTQ-1 | Fa0/3 | AP-BHTQ-1 | Port 0 | Đồng thẳng |
| 79 | SW-BHTQ-1 | Fa0/4 | CAM-BHTQ | Fa0 | Đồng thẳng |
| 80 | SW-BHTQ-1 | Fa0/5 | PHONE-BHTQ | Fa0 | Đồng thẳng |
| 81 | SW-BHTQ-1 | Fa0/6 | PC-BHTQ-CLINIC-2 | Fa0 | Đồng thẳng |
| 82 | SW-BHTQ-2 | Fa0/1 | PC-BHTQ-ADMIN | Fa0 | Đồng thẳng |
| 83 | SW-BHTQ-2 | Fa0/2 | PC-BHTQ-IT | Fa0 | Đồng thẳng |
| 84 | SW-BHTQ-2 | Fa0/3 | MED-BHTQ | Fa0 | Đồng thẳng |
| 85 | SW-BHTQ-2 | Fa0/4 | SRV-BHTQ | Fa0 | Đồng thẳng |
| 86 | SW-BHTQ-2 | Fa0/5 | AP-BHTQ-2 | Port 0 | Đồng thẳng |
