import os
import sys
import io
from dotenv import load_dotenv
from anthropic import Anthropic
from datetime import datetime

# 强制解决控制台中文显示问题
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

class NetworkConfigGenerator:
    def __init__(self):
        print(f"\n[Step 1: 初始化] 正在从 .env 加载 API Key...")
        api_key = os.getenv('ANTHROPIC_API_KEY')
        # 创建客户端实例，这是后续所有调用的基础
        self.client = Anthropic(api_key=api_key)
        print(f" -> 客户端已就绪。")

    def generate_config(self, vendor, config_type, custom_requirements=''):
        print(f"\n[Step 2: 调用 generate_config 函数]")
        print(f" -> 接收到参数: Vendor={vendor}, Type={config_type}")
        
        # 跳转到 _build_prompt
        print(f" -> 准备构建发送给 AI 的指令内容...")
        prompt = self._build_prompt(vendor, config_type, custom_requirements)
        
        print("-" * 30)
        print(f"[Step 3: 最终发送的报文主体 (Payload)]\n{prompt}")
        print("-" * 30)
        
        print(f"\n[Step 4: 发送请求] 正在通过 HTTPS POST 发送到 Anthropic 服务器...")
        try:
            # 这里的 client.messages.create 实际上封装了我们之前学习的 headers 和 json 构造过程
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            print(f" -> 服务器响应成功！收到状态码: 200")
            # 这里的 message.content[0].text 是从复杂的 JSON 结构中提取文字
            return message.content[0].text
            
        except Exception as e:
            print(f" -> [错误捕获] 发送过程中出现异常: {e}")
            return f"生成失败: {e}"

    def _build_prompt(self, vendor, config_type, custom_req):
        print(f" -> [子任务: _build_prompt] 正在将输入数据套入专家模板...")
        base_prompt = f"""
作为网络配置专家，请为以下需求生成配置：
厂商: {vendor}
配置类型: {config_type}
额外需求: {custom_req if custom_req else '无'}
要求：1.完整可用 2.详细注释 3.安全标准。直接输出代码。
"""
        return base_prompt

    def save_config(self, config, vendor, config_type):
        print(f"\n[Step 5: 保存文件] 开始持久化存储...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"configs/{vendor}_{config_type}_{timestamp}.txt"
        
        print(f" -> 检查并创建目录: configs/")
        os.makedirs('configs', exist_ok=True)
        
        print(f" -> 正在写入文件: {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(config)
        return filename

def main():
    print("=== 启动程序主入口 main() ===")
    generator = NetworkConfigGenerator()
    
    vendor = input("\n请选择厂商 (如 cisco): ")
    config_type = input("请输入配置类型 (如 vlan): ")
    custom_req = input("需求描述: ")
    
    # 逻辑流转：main -> generator.generate_config
    config = generator.generate_config(vendor, config_type, custom_req)
    
    print("\n[Step 6: 展示结果] 以下是 AI 生成的内容预览：")
    print(config[:100] + "...") # 只预览前100字
    
    save = input("\n是否保存？(y/n): ")
    if save.lower() == 'y':
        # 逻辑流转：main -> generator.save_config
        fname = generator.save_config(config, vendor, config_type)
        print(f" -> 完成！文件路径: {fname}")

if __name__ == "__main__":
    main()