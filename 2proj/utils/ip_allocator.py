import json
import re
import os

def allocate_ips(json_path):
    if not os.path.exists(json_path):
        print(f"错误: 找不到文件 {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def get_node_info(node_id):
        # 使用正则表达式提取 ID 中的数字，例如 "R1" -> 1, "FW7" -> 7
        match = re.search(r'\d+', node_id)
        return int(match.group()) if match else 0

    print("\n[IP 分配启动] 正在根据设备 ID 计算 192.168.x.y/30 地址...")

    for link in data.get('links', []):
        # 提取源和目的节点 ID (例如 R1:Gi0/0 -> R1)
        src_node = link['source'].split(':')[0]
        dst_node = link['target'].split(':')[0]
        
        # 获取设备编号 (y1, y2)
        y1 = get_node_info(src_node)
        y2 = get_node_info(dst_node)
        
        # 按照规则 2 计算 x (两台设备代码组合，通常从小到大排序以保证子网一致)
        # 例如 R1和R2连接，x = 12；R2和R1连接，x 依然是 12
        ids = sorted([y1, y2])
        x = int(f"{ids[0]}{ids[1]}")
        
        # 规则 1 & 3: 生成网络地址和具体的接口 IP
        # 网络地址通常为 .0 (在 /30 中，这里我们简化处理，将 x 作为第三段)
        link['network'] = f"192.168.{x}.0/30"
        link['source_ip'] = f"192.168.{x}.{y1}"
        link['target_ip'] = f"192.168.{x}.{y2}"
        
        print(f"  链路 {src_node} <-> {dst_node}: 子网 192.168.{x}.0/30 | {src_node}: .{y1} | {dst_node}: .{y2}")

    # 写回文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("\n[成功] IP 地址已成功写入 JSON 文件。")

if __name__ == "__main__":
    allocate_ips('data/current_topo.json')