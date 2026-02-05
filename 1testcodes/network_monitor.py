import json
import time
import hashlib
import os
from pyvis.network import Network

# --- 配置区 ---
JSON_FILE = 'topology.json'
HTML_FILE = 'topology_monitor.html'
CHECK_INTERVAL = 2  # 检查文件是否有变动的频率（秒）
REFRESH_RATE = 5    # 浏览器端自动刷新的频率（秒）

def get_file_hash(file_path):
    """计算文件的 MD5 值，用于判断内容是否有变化"""
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def generate_visual_topo():
    """读取 JSON 并生成带自动刷新标签的 HTML"""
    print(f"[{time.strftime('%H:%M:%S')}] 检测到状态变化，正在更新拓扑图...")
    
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取 JSON 失败: {e}")
        return

    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
    router_icon = "https://img.icons8.com/fluency/96/server.png" 
    
    COLOR_UP, COLOR_DOWN = "#2ecc71", "#e74c3c"
    LINE_NORMAL, LINE_DOWN = "#2980b9", "#95a5a6"

    # 添加节点
    for node in data['nodes']:
        net.add_node(node['id'], label=node['id'], shape='image', image=router_icon, size=40)

    # 添加链路与接口点
    def find_intf(r_id, i_name):
        for n in data['nodes']:
            if n['id'] == r_id:
                for i in n.get('interfaces', []):
                    if i['name'] == i_name: return i
        return {"status": "up", "ip": "N/A", "mask": "N/A"}

    for link in data['links']:
        src_node, src_intf = link['source'].split(':')
        dst_node, dst_intf = link['target'].split(':')
        s_info, d_info = find_intf(src_node, src_intf), find_intf(dst_node, dst_intf)
        s_pt, d_pt = f"{src_node}_{src_intf}_pt", f"{dst_node}_{dst_intf}_pt"

        # 接口点 (根据 JSON 里的 status 决定红/绿)
        net.add_node(s_pt, label=" ", title=f"{src_intf}\n{s_info['ip']}\n{s_info['status'].upper()}",
                     shape='dot', size=7, color=COLOR_UP if s_info['status'] == 'up' else COLOR_DOWN)
        net.add_node(d_pt, label=" ", title=f"{dst_intf}\n{d_info['ip']}\n{d_info['status'].upper()}",
                     shape='dot', size=7, color=COLOR_UP if d_info['status'] == 'up' else COLOR_DOWN)

        # 连线
        is_down = (s_info['status'] == 'down' or d_info['status'] == 'down')
        net.add_edge(src_node, s_pt, color='#bdc3c7', length=12, springConstant=0.6)
        net.add_edge(dst_node, d_pt, color='#bdc3c7', length=12, springConstant=0.6)
        net.add_edge(s_pt, d_pt, label=link['network'], color=LINE_DOWN if is_down else LINE_NORMAL, 
                     width=4, length=300, dashes=is_down)

    net.set_options('{"physics": {"barnesHut": {"gravitationalConstant": -4000, "springLength": 220}}}')
    
    net.save_graph(HTML_FILE)
    
    # 注入 Meta 刷新标签
    with open(HTML_FILE, 'r+', encoding='utf-8') as f:
        html_content = f.read()
        refresh_meta = f'\n<meta http-equiv="refresh" content="{REFRESH_RATE}">\n'
        if "<head>" in html_content and refresh_meta not in html_content:
            new_content = html_content.replace("<head>", "<head>" + refresh_meta)
            f.seek(0); f.write(new_content); f.truncate()

# --- 主循环：监听文件变化 ---
if __name__ == "__main__":
    print(f"📡 实时监听模式已启动。正在监听 {JSON_FILE}...")
    print(f"请在浏览器打开: {HTML_FILE}")
    
    last_hash = None
    
    try:
        while True:
            current_hash = get_file_hash(JSON_FILE)
            
            # 只有当文件内容发生变化时，才重新渲染
            if current_hash != last_hash:
                generate_visual_topo()
                last_hash = current_hash
            
            time.sleep(CHECK_INTERVAL) # 每2秒检查一次文件指纹
    except KeyboardInterrupt:
        print("\n监听已停止。")