import os
from dotenv import load_dotenv
from anthropic import Anthropic
from datetime import datetime

load_dotenv()

class NetworkConfigGenerator:
    """网络配置生成器"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.templates = {
            'cisco_init': '基础初始化配置',
            'cisco_security': '端口安全配置',
            'cisco_vlan': 'VLAN配置',
            'huawei_init': '华为初始化配置',
            'huawei_security': '华为端口安全配置',
        }
    
    def generate_config(self, vendor, config_type, custom_requirements=''):
        """
        生成配置
        
        参数:
            vendor: 厂商 (cisco/huawei/juniper)
            config_type: 配置类型
            custom_requirements: 用户自定义需求
        """
        prompt = self._build_prompt(vendor, config_type, custom_requirements)
        
        print("正在生成配置，请稍候...")
        
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
            return f"生成失败: {e}"
    
    def _build_prompt(self, vendor, config_type, custom_req):
        """构建提示词"""
        base_prompt = f"""
作为网络配置专家，请为以下需求生成配置：

厂商: {vendor}
配置类型: {config_type}
额外需求: {custom_req if custom_req else '无'}

要求：
1. 生成完整可用的配置
2. 添加详细的注释说明每个部分的作用
3. 指出哪些参数需要根据实际环境修改
4. 包含必要的安全最佳实践
5. 配置要符合实际生产环境标准

请直接输出配置代码，不需要额外的解释文字。
"""
        return base_prompt
    
    def save_config(self, config, vendor, config_type):
        """保存配置到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"configs/{vendor}_{config_type}_{timestamp}.txt"
        
        # 确保configs目录存在
        os.makedirs('configs', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(config)
        
        return filename

def main():
    """主程序"""
    print("=== 网络配置自动生成器 V2.0 ===\n")
    
    generator = NetworkConfigGenerator()
    
    # 获取用户输入
    print("支持的厂商: cisco, huawei, juniper")
    vendor = input("请选择厂商: ").lower()
    
    print("\n配置类型示例: init(初始化), security(安全), vlan, ospf, bgp")
    config_type = input("请输入配置类型: ").lower()
    
    print("\n请描述您的具体需求（可选，直接回车跳过）:")
    custom_req = input("需求: ")
    
    # 生成配置
    config = generator.generate_config(vendor, config_type, custom_req)
    
    # 显示配置
    print("\n" + "="*60)
    print("生成的配置：")
    print("="*60)
    print(config)
    print("="*60)
    
    # 保存配置
    save = input("\n是否保存配置？(y/n): ")
    if save.lower() == 'y':
        filename = generator.save_config(config, vendor, config_type)
        print(f"\n✓ 配置已保存到: {filename}")

if __name__ == "__main__":
    main()