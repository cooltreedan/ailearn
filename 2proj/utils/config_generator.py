import json
import os
import re

def generate_configs(json_path):
    if not os.path.exists(json_path):
        return
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not os.path.exists('configs'):
        os.makedirs('configs')

    nodes = data.get('nodes', [])
    links = data.get('links', [])

    for node in nodes:
        n_id = node['id']
        brand = node['brand'].lower()
        n_type = node['type'].lower()
        
        # 获取设备编号用于 Loopback (例如 R1 -> 1)
        n_num = re.search(r'\d+', n_id).group() if re.search(r'\d+', n_id) else "0"
        loop_ip = f"{n_num}.{n_num}.{n_num}.{n_num}"
        
        config = []

        # ==========================================
        # 1. 基础配置 & 管理加固 (Cisco/Arista)
        # ==========================================
        if brand in ['cisco', 'arista']:
            config.extend([
                f"hostname {n_id}",
                "service password-encryption",
                "enable secret Admin@1234",
                "username admin privilege 15 secret Admin@1234",
                # 时区设置 (PST UTC-8)
                "clock timezone PST -8 0",
                # 基础设施服务器
                "ntp server 192.168.100.1",
                "logging host 192.168.100.2",
                "snmp-server community public RO",
                "snmp-server host 192.168.100.3 version 2c public",
                # SSH v2 配置
                "ip domain-name lab.local",
                "ip ssh version 2",
                "line vty 0 15",
                " password Admin@1234",
                " login local",
                " transport input ssh",  # 禁用 Telnet，只允许 SSH
                "exit"
            ])

        # ==========================================
        # 2. 接口配置 (含 IP、描述、启用)
        # ==========================================
        # 配置 Loopback 接口作为 Router-ID
        if brand in ['cisco', 'arista']:
            config.extend([
                "interface Loopback0",
                " description Router-ID_Loopback",
                f" ip address {loop_ip} 255.255.255.255",
                "exit"
            ])

        # 配置物理接口
        node_links = [l for l in links if l['source'].startswith(n_id) or l['target'].startswith(n_id)]
        for link in node_links:
            is_src = link['source'].startswith(n_id)
            local_intf = link['source'].split(':')[1] if is_src else link['target'].split(':')[1]
            remote_full = link['target'] if is_src else link['source']
            ip = link.get('source_ip', '0.0.0.0') if is_src else link.get('target_ip', '0.0.0.0')
            
            if brand in ['cisco', 'arista']:
                config.extend([
                    f"interface {local_intf}",
                    f" description Connected_to_{remote_full.replace(':', '_')}", # 接口描述
                    f" ip address {ip} 255.255.255.252",
                    " no shutdown",
                    "exit"
                ])
            elif brand == 'paloalto':
                # Palo Alto 接口配置 (CLI)
                config.extend([
                    f"set network interface ethernet {local_intf} layer3 ip {ip}/30",
                    f"set network interface ethernet {local_intf} comment Connected_to_{remote_full.replace(':', '_')}"
                ])

        # ==========================================
        # 3. OSPF 路由配置 (Area 0)
        # ==========================================
        if "router" in n_type or "switch" in n_type:
            if brand == 'cisco':
                config.extend([
                    "router ospf 1",
                    f" router-id {loop_ip}",
                    " network 0.0.0.0 255.255.255.255 area 0",
                    "exit"
                ])
            elif brand == 'arista':
                config.extend([
                    "router ospf 1",
                    f" router-id {loop_ip}",
                    " network 0.0.0.0/0 area 0",
                    "exit"
                ])

        # ==========================================
        # 4. 防火墙特有配置 (Palo Alto)
        # ==========================================
        if brand == 'paloalto':
            config.extend([
                f"set deviceconfig system hostname {n_id}",
                "set deviceconfig system timezone US/Pacific", # PST
                "set deviceconfig system ntp-servers primary-ntp address 192.168.100.1",
                "set mgt-config users admin password Admin@1234",
                "set mgt-config users admin permissions role-based superuser yes",
                # 安全策略: 允许内部到外部的 HTTP/HTTPS
                "set rulebase security rules Trust-to-Untrust service [ service-http service-https ] action allow"
            ])

        # 写入文件
        final_config_text = "\n".join(config)
        
        with open(f"configs/{n_id}.txt", 'w', encoding='utf-8') as cf:
            cf.write(final_config_text)
            
    print(f">>> 已完成所有设备的初始化配置生成。")

if __name__ == "__main__":
    generate_configs('data/current_topo.json')