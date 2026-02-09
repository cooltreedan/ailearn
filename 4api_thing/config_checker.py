import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

class ConfigChecker:
    """配置文件审查器"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def check_config(self, config_content):
        """
        检查配置文件
        
        参数:
            config_content: 配置文件内容
        """
        prompt = f"""
作为资深网络安全专家，请审查以下网络设备配置，找出：

1. 安全隐患（如明文密码、弱加密、开放的危险服务）
2. 不符合最佳实践的地方
3. 可能导致故障的配置
4. 性能优化建议

配置内容：
{config_content}

请按以下格式输出：

【严重问题】
- 问题1：...
  建议：...

【警告】
- 问题1：...
  建议：...

【优化建议】
- 建议1：...
"""
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"检查失败: {e}"

def main():
    print("=== 网络配置审查工具 ===\n")
    
    checker = ConfigChecker()
    
    # 选择输入方式
    print("1. 直接粘贴配置")
    print("2. 读取配置文件")
    choice = input("\n请选择 (1/2): ")
    
    if choice == '1':
        print("\n请粘贴配置（输入END结束）：")
        lines = []
        while True:
            line = input()
            if line == 'END':
                break
            lines.append(line)
        config_content = '\n'.join(lines)
    
    elif choice == '2':
        filepath = input("请输入配置文件路径: ")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config_content = f.read()
        except Exception as e:
            print(f"读取文件失败: {e}")
            return
    else:
        print("无效选择")
        return
    
    # 执行检查
    print("\n正在分析配置，请稍候...\n")
    result = checker.check_config(config_content)
    
    # 显示结果
    print("="*60)
    print("审查结果：")
    print("="*60)
    print(result)
    print("="*60)
    
    # 保存报告
    save = input("\n是否保存审查报告？(y/n): ")
    if save.lower() == 'y':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/config_check_{timestamp}.txt"
        os.makedirs('reports', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✓ 报告已保存到: {filename}")

if __name__ == "__main__":
    from datetime import datetime
    main()