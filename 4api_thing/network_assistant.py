import os
from dotenv import load_dotenv
from config_generator_v2 import NetworkConfigGenerator
from config_checker import ConfigChecker
from batch_processor import BatchProcessor

load_dotenv()

def show_menu():
    """显示主菜单"""
    print("\n" + "="*60)
    print("         网络配置AI助手 V2.0")
    print("="*60)
    print("1. 生成单个配置")
    print("2. 检查配置文件")
    print("3. 批量生成配置")
    print("4. AI对话模式（问答任何网络问题）")
    print("5. 配置模板库（查看已有模板）")
    print("0. 退出")
    print("="*60)

def chat_mode():
    """AI对话模式"""
    from ai_chat import chat_with_ai
    
    print("\n=== AI网络专家对话模式 ===")
    print("您可以问任何网络相关的问题")
    print("输入 'back' 返回主菜单\n")
    
    while True:
        question = input("您的问题: ")
        if question.lower() == 'back':
            break
        if not question.strip():
            continue
        
        print("\n思考中...\n")
        answer = chat_with_ai(question)
        print(f"AI: {answer}\n")
        print("-"*60)

def view_templates():
    """查看配置模板库"""
    templates_dir = 'configs'
    if not os.path.exists(templates_dir):
        print("还没有保存的配置模板")
        return
    
    files = [f for f in os.listdir(templates_dir) if f.endswith('.txt')]
    if not files:
        print("模板库为空")
        return
    
    print(f"\n找到 {len(files)} 个配置模板：")
    for idx, filename in enumerate(files, 1):
        print(f"{idx}. {filename}")
    
    view = input("\n输入序号查看详情（回车返回）: ")
    if view.isdigit() and 1 <= int(view) <= len(files):
        filepath = os.path.join(templates_dir, files[int(view)-1])
        with open(filepath, 'r', encoding='utf-8') as f:
            print("\n" + "="*60)
            print(f.read())
            print("="*60)

def main():
    """主程序"""
    generator = NetworkConfigGenerator()
    checker = ConfigChecker()
    batch = BatchProcessor()
    
    while True:
        show_menu()
        choice = input("\n请选择功能 (0-5): ")
        
        if choice == '0':
            print("\n感谢使用，再见！")
            break
        
        elif choice == '1':
            # 生成单个配置
            print("\n=== 配置生成 ===")
            vendor = input("厂商 (cisco/huawei/juniper): ")
            config_type = input("配置类型: ")
            custom = input("特殊需求（可选）: ")
            
            config = generator.generate_config(vendor, config_type, custom)
            print("\n" + "="*60)
            print(config)
            print("="*60)
            
            if input("\n保存？(y/n): ").lower() == 'y':
                filename = generator.save_config(config, vendor, config_type)
                print(f"✓ 已保存: {filename}")
        
        elif choice == '2':
            # 检查配置
            print("\n=== 配置检查 ===")
            filepath = input("配置文件路径: ")
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                result = checker.check_config(content)
                print("\n" + result)
            except Exception as e:
                print(f"错误: {e}")
        
        elif choice == '3':
            # 批量生成
            print("\n=== 批量生成 ===")
            print("功能开发中...")
            # 调用batch_processor的main函数
        
        elif choice == '4':
            # 对话模式
            chat_mode()
        
        elif choice == '5':
            # 查看模板
            view_templates()
        
        else:
            print("无效选择")
        
        input("\n按回车继续...")

if __name__ == "__main__":
    main()