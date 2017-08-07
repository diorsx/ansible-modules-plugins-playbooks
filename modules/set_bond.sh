#!/bin/bash
#Type: modules
#Auther: wood
#Desc: 批量配置网卡bond
#Date: 2017年5月8日10:10:30
set -e
source ${1}

#初始化参数
bond0_ipaddr=$ipv4_address
bond0_netmask=$ipv4_netmask
bond0_gateway=$gateway
os_version=$os_version
interface_counts=$interface_counts
interfaces=$interfaces

if (( $interface_counts<3 ))
    then
    printf '{"failed": %s, "msg": "there are no netcard, %s netcards"}' "true" "$interface_counts" 
    exit 1
fi

function Add_bond()
{
    cat >ifcfg-bond0 <<EOF
DEVICE=bond0
TYPE=Ethernet
ONBOOT=yes
BOOTPROTO=static
NM_CONTROLLED=no
IPADDR=$bond0_ipaddr
NETMASK=$bond0_netmask
GATEWAY=$bond0_gateway
BONDING_OPTS="mode=1 miimon=100"
USERCTL=no
EOF
}

function Add_slave()
{
    netcard_name=$1
    cat >ifcfg-${netcard_name} <<EOF
DEVICE=${netcard_name}
TYPE=Ethernet
BOOTPROTO=none
ONBOOT=yes
MASTER=bond0
SLAVE=yes
USERCTL=no
EOF
}

MODPROBE="/sbin/modprobe"
cd /etc/sysconfig/network-scripts

for interface in $interfaces
do
    if [[ "$interface" !="lo" && -f ifcfg-${interface} ]]
        then
            cp ifcfg-${interface} ifcfg-${interface}.bak
            Add_slave ${interface}

    fi
done

Add_bond

echo "alias bond0 bonding">>/etc/modprobe.d/dist.conf 
echo "options bond0 mode=1 miimon=100">>/etc/modprobe.d/dist.conf 
 
#$MODPROBE bonding

#/etc/init.d/network restart
#echo "-----------------------bond0主备状态------------------"
#more /proc/net/bonding/bond0

printf '{"failed": %s, "changed": %s, msg": "success"}' "false" "true"
exit 0