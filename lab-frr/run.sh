#!/bin/bash
cd "$(dirname "$0")"
exec > >(tee run.log) 2>&1
clab(){ docker run --rm --privileged --network host --pid host -v /var/run/docker.sock:/var/run/docker.sock -v /var/run/netns:/var/run/netns -v /etc/hosts:/etc/hosts -v /var/lib/docker/containers:/var/lib/docker/containers -v "$PWD":"$PWD" -w "$PWD" ghcr.io/srl-labs/clab containerlab "$@"; }
docker info >/dev/null 2>&1 || { echo "Docker chua chay"; exit 1; }
echo "== destroy cu =="; clab destroy -t tvi-frr.clab.yml --cleanup
echo "== deploy =="; clab deploy -t tvi-frr.clab.yml
echo "== cho BGP =="; sleep 20
for n in isp hcm hn dn; do echo "== $n: bgp summary =="; docker exec clab-tvi-$n vtysh -c "show ip bgp summary"; done
echo "== isp: routes =="; docker exec clab-tvi-isp vtysh -c "show ip route bgp"
echo "== ping hcm->isp =="; docker exec clab-tvi-hcm ping -c2 10.0.1.1
echo "XONG"
