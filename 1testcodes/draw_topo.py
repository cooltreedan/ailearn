import json
import time
import random
import os
from pyvis.network import Network

# --- 配置区 ---
JSON_FILE = 'topology.json'
HTML_FILE = 'topology_monitor.html'
REFRESH_INTERVAL = 5  # 秒

def simulate_network_changes():
    """模拟随机的网络接口状态变化并更新 JSON 文件"""
    if not os.path.exists(JSON_FILE):
        print(f"错误: 找不到 {JSON_FILE}。请确保文件存在。")
        return False

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 随机选择一个路由器和接口进行状态翻转
    node = random.choice(data['nodes'])
    if node['interfaces']:
        intf = random.choice(node['interfaces'])
        # 随机切换状态 (80% 几率 Up, 20% 几率 Down，模拟真实稳定性)
        intf['status'] = "up" if random.random() > 0.2 else "down"

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return True

def generate_visual_topo():
    """读取 JSON 并生成带自动刷新标签的 HTML"""
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
    router_icon = "https://img.icons8.com/fluency/96/server.png" 
    
    # 颜色定义
    COLOR_UP, COLOR_DOWN = "#2ecc71", "#e74c3c"
    LINE_NORMAL, LINE_DOWN = "#2980b9", "#95a5a6"

    # 添加节点
    for node in data['nodes']:
        net.add_node(node['id'], label=node['id'], shape='image', image=router_icon, size=40)

    # 添加链路与接口点
    for link in data['links']:
        src_node, src_intf = link['source'].split(':')
        dst_node, dst_intf = link['target'].split(':')
        
        # 查找接口详细数据
        def find_intf(r_id, i_name):
            for n in data['nodes']:
                if n['id'] == r_id:
                    for i in n['interfaces']:
                        if i['name'] == i_name: return i
            return {"status": "up", "ip": "N/A", "mask": "N/A"}

        s_info, d_info = find_intf(src_node, src_intf), find_intf(dst_node, dst_intf)
        s_pt, d_pt = f"{src_node}_{src_intf}_pt", f"{dst_node}_{dst_intf}_pt"

        # 接口点逻辑
        net.add_node(s_pt, label=" ", title=f"{src_intf}\n{s_info['ip']}\n{s_info['status'].upper()}",
                     shape='dot', size=7, color=COLOR_UP if s_info['status'] == 'up' else COLOR_DOWN)
        net.add_node(d_pt, label=" ", title=f"{dst_intf}\n{d_info['ip']}\n{d_info['status'].upper()}",
                     shape='dot', size=7, color=COLOR_UP if d_info['status'] == 'up' else COLOR_DOWN)

        # 线条逻辑
        is_down = (s_info['status'] == 'down' or d_info['status'] == 'down')
        net.add_edge(src_node, s_pt, color='#bdc3c7', length=12, springConstant=0.6)
        net.add_edge(dst_node, d_pt, color='#bdc3c7', length=12, springConstant=0.6)
        net.add_edge(s_pt, d_pt, label=link['network'], color=LINE_DOWN if is_down else LINE_NORMAL, 
                     width=4, length=300, dashes=is_down)

    net.set_options('{"physics": {"barnesHut": {"gravitationalConstant": -4000, "springLength": 220}}}')
    
    # 保存并注入刷新脚本
    net.save_graph(HTML_FILE)
    
    with open(HTML_FILE, 'r+', encoding='utf-8') as f:
        html_content = f.read()
        # 注入 Meta 刷新标签
        refresh_meta = f'\n<meta http-equiv="refresh" content="{REFRESH_INTERVAL}">\n'
        if "<head>" in html_content:
            new_content = html_content.replace("<head>", "<head>" + refresh_meta)
            f.seek(0)
            f.write(new_content)
            f.truncate()

# --- 主循环 ---
if __name__ == "__main__":
    print(f"🚀 实时监控已启动。请在浏览器中打开: {HTML_FILE}")
    print("按 Ctrl+C 停止监控。")
    try:
        while True:
            if simulate_network_changes():
                generate_visual_topo()
                print(f"[{time.strftime('%H:%M:%S')}] 状态已更新，页面将在下一周期刷新...")
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 监控已停止。")