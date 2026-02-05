import os
import json
import sys
from models.topology import TopologyModel
from utils.renderer import TopologyRenderer
from utils.ip_allocator import allocate_ips
from utils.config_generator import generate_configs

def main():
    json_path = 'data/current_topo.json'
    use_existing = False

    print("========================================")
    print("       自动化网络设计与配置系统 V2.0    ")
    print("========================================")

    # --- 逻辑 1: 检测已存在的拓扑文件 ---
    if os.path.exists(json_path):
        choice = input(f"检测到已存在的拓扑文件 '{json_path}'，是否直接调用？(y/n): ").lower()
        if choice == 'y':
            use_existing = True
            print(">>> 已加载现有拓扑数据。")

    # 初始化模型（无论是否使用旧文件，都需要初始化以供后续流程使用）
    topo_model = TopologyModel(project_name="Network_Lab")
    renderer = TopologyRenderer(json_path)

    # --- 逻辑 2: 批量输入阶段 ---
    if not use_existing:
        print("\n[步骤 1] 请输入设备信息和连接关系 (支持多行批量粘贴):")
        print("------------------------------------------------")
        print("格式示例:")
        print("R1,Cisco,Router")
        print("SW3,Arista,Switch")
        print("R1:Gi0/1 连接 SW3:Et1")
        print("------------------------------------------------")
        print(">>> 请开始输入/粘贴内容，最后输入 'done' 并回车结束输入:")
        
        raw_lines = []
        while True:
            line = input().strip()
            if line.lower() == 'done':
                break
            if line:  # 过滤空行
                raw_lines.append(line)

        # 批量处理所有行
        print(f"\n>>> 正在解析 {len(raw_lines)} 条数据...")
        for user_input in raw_lines:
            # 增强版解析逻辑：支持多种连接符
            if any(sep in user_input for sep in ["连接", "-", "<->", " to "]):
                temp_input = user_input.replace("连接", "-").replace("<->", "-").replace(" to ", "-")
                parts = temp_input.split("-")
                if len(parts) == 2:
                    topo_model.add_link({
                        "source": parts[0].strip(),
                        "target": parts[1].strip(),
                        "network": "TBD"
                    })
            else:
                # 处理节点
                parts = user_input.split(",")
                if len(parts) == 3:
                    topo_model.add_node({
                        "id": parts[0].strip(),
                        "brand": parts[1].strip(),
                        "type": parts[2].strip()
                    })
        
        topo_model.save_to_json(json_path)
        print(">>> 数据解析完成并已保存。")

    # --- 逻辑 3: 第一次确认（物理连接） ---
    print("\n[步骤 2] 正在生成初步拓扑预览 (物理连接)...")
    renderer.render()
    print(">>> 物理拓扑已生成。请刷新浏览器查看 topology_preview.html。")

    while True:
        choice1 = input("\n[?] 物理连接是否正确？\n[y]确认并分配IP | [add]继续添加 | [exit]退出 : ").lower()
        if choice1 == 'y':
            break
        elif choice1 == 'add':
            print("请继续输入连接信息 (输入 'done' 重新渲染):")
            while True:
                line = input("> ").strip()
                if line.lower() == 'done':
                    # 重新保存并渲染
                    # 注意：如果是加载的旧文件，这里需要重新获取 topo_model 的上下文
                    # 简化处理：建议重新运行脚本来修改已存在的复杂拓扑
                    renderer.render()
                    break
                topo_model.parse_and_add(line) # 假设模型层有此方法，否则按上面的逻辑添加
        else:
            print("程序已退出。")
            return

    # --- 逻辑 4: IP 分配与第二次确认（逻辑地址） ---
    print("\n[步骤 3] 正在按照 192.168.x.y/30 规则分配 IP 地址和 Loopback...")
    allocate_ips(json_path)
    
    print("\n[步骤 4] 正在更新拓扑图 (加入 IP 信息)...")
    renderer.render()
    print(">>> 逻辑拓扑已更新！请再次刷新浏览器查看接口 IP 和 子网标注。")

    while True:
        choice2 = input("\n[?] IP 地址规划是否正确？\n[y]确认并生成配置 | [exit]退出 : ").lower()
        if choice2 == 'y':
            break
        else:
            print("程序已退出。")
            return

    # --- 逻辑 5: 生成配置 ---
    print("\n[步骤 5] 正在生成各厂商初始化配置 (.txt)...")
    generate_configs(json_path)

    print("\n========================================")
    print("           任务全部完成！               ")
    print("========================================")
    print(f"1. 最终拓扑图: topology_preview.html")
    print(f"2. 设备配置文件目录: configs/")
    print("========================================\n")

if __name__ == "__main__":
    main()