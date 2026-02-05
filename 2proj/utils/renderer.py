import json
import os
from pyvis.network import Network

class TopologyRenderer:
    def __init__(self, json_path):
        self.json_path = json_path

    def render(self, output_html="topology_preview.html"):
        """支持双重确认逻辑的渲染器"""
        if not os.path.exists(self.json_path):
            return

        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="#34495e")
        BRAND_CONFIG = {"cisco": "#2980b9", "arista": "#27ae60", "paloalto": "#c0392b", "default": "#7f8c8d"}

        # 1. 渲染设备
        for node in data.get('nodes', []):
            n_id = node.get('id')
            raw_brand = str(node.get('brand', 'default')).lower()
            n_type = str(node.get('type', 'default')).lower()
            color = BRAND_CONFIG.get(raw_brand, BRAND_CONFIG["default"])
            
            # 形状判断改进：使用 in 关键字适配 "Router/Switch" 等组合类型
            if "router" in n_type or "rt" in n_type:
                shape, t_label = "dot", "Router"
            elif "switch" in n_type or "sw" in n_type:
                shape, t_label = "box", "Switch"
            elif "firewall" in n_type or "fw" in n_type:
                shape, t_label = "diamond", "Firewall"
            else:
                shape, t_label = "ellipse", n_type.capitalize()

            net.add_node(n_id, label=n_id, shape=shape, color=color, size=20, title=f"{raw_brand.upper()} - {t_label}")

        # 2. 渲染连线与辅助点
        for i, link in enumerate(data.get('links', [])):
            u_full, v_full = link['source'], link['target']
            u, v = u_full.split(':')[0], v_full.split(':')[0]
            u_intf = u_full.split(':')[1] if ':' in u_full else ""
            v_intf = v_full.split(':')[1] if ':' in v_full else ""
            
            # IP 信息处理 (KeyError 防御逻辑)
            u_ip = link.get('source_ip', '')
            v_ip = link.get('target_ip', '')
            subnet = link.get('network', '')

            u_suffix = f"(.{u_ip.split('.')[-1]})" if u_ip and '.' in u_ip else ""
            v_suffix = f"(.{v_ip.split('.')[-1]})" if v_ip and '.' in v_ip else ""
            subnet_label = f"[{subnet}]" if subnet and subnet.upper() != 'TBD' else ""

            # 辅助点定位
            anchor_u, anchor_v = f"anchor_{i}_u", f"anchor_{i}_v"
            net.add_node(anchor_u, label=f"{u_intf}{u_suffix}", shape="dot", size=1, color="rgba(0,0,0,0)", font={'size': 10, 'vadjust': -15})
            net.add_node(anchor_v, label=f"{v_intf}{v_suffix}", shape="dot", size=1, color="rgba(0,0,0,0)", font={'size': 10, 'vadjust': -15})

            net.add_edge(u, anchor_u, length=25, color="rgba(0,0,0,0)", physics=True)
            net.add_edge(v, anchor_v, length=25, color="rgba(0,0,0,0)", physics=True)

            # 错位偏移防止重叠
            v_off = (i % 3 - 1) * 18
            net.add_edge(anchor_u, anchor_v, label=subnet_label, color="#bdc3c7", width=1.5, 
                         font={'size': 10, 'align': 'horizontal', 'background': '#ffffff', 'vadjust': v_off},
                         smooth={'enabled': False})

        net.set_options('{"physics":{"enabled":true,"barnesHut":{"gravitationalConstant":-5000,"springLength":280}}}')
        net.save_graph(output_html)