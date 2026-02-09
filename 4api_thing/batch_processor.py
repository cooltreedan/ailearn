import os
from dotenv import load_dotenv
from anthropic import Anthropic
from datetime import datetime
import time

load_dotenv()

class BatchProcessor:
    """批量处理工具"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def batch_generate_configs(self, config_list):
        """
        批量生成配置
        
        参数:
            config_list: 配置需求列表
            格式: [
                {'vendor': 'cisco', 'type': 'init', 'desc': '核心交换机'},
                {'vendor': 'huawei', 'type': 'ospf', 'desc': '边界路由器'},
                ...
            ]
        """
        results = []
        total = len(config_list)
        
        for idx, config_req in enumerate(config_list, 1):
            print(f"\n[{idx}/{total}] 正在生成: {config_req['desc']}")
            
            prompt = f"""
生成{config_req['vendor']}设备的{config_req['type']}配置
用途: {config_req['desc']}
要求: 生产环境标准，包含注释和安全配置
"""
            
            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result = {
                    'desc': config_req['desc'],
                    'vendor': config_req['vendor'],
                    'type': config_req['type'],
                    'config': message.content[0].text,
                    'status': 'success'
                }
                
                print(f"  ✓ 完成")
                
            except Exception as e:
                result = {
                    'desc': config_req['desc'],
                    'status': 'failed',
                    'error': str(e)
                }
                print(f"  ✗ 失败: {e}")
            
            results.append(result)
            
            # 避免API调用过快
            if idx < total:
                time.sleep(1)
        
        return results
    
    def save_batch_results(self, results):
        """保存批量处理结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"batch_output_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存每个配置
        for idx, result in enumerate(results, 1):
            if result['status'] == 'success':
                filename = f"{output_dir}/{idx:02d}_{result['vendor']}_{result['type']}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {result['desc']}\n\n")
                    f.write(result['config'])
        
        # 生成总结报告
        summary_file = f"{output_dir}/00_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("批量生成配置总结\n")
            f.write("="*60 + "\n\n")
            f.write(f"生成时间: {datetime.now()}\n")
            f.write(f"总数: {len(results)}\n")
            f.write(f"成功: {sum(1 for r in results if r['status']=='success')}\n")
            f.write(f"失败: {sum(1 for r in results if r['status']=='failed')}\n\n")
            
            for idx, result in enumerate(results, 1):
                status = "✓" if result['status'] == 'success' else "✗"
                f.write(f"{status} {idx}. {result['desc']}\n")
        
        return output_dir

def main():
    print("=== 批量配置生成工具 ===\n")
    
    # 示例：一次生成多个设备的配置
    config_requests = [
        {
            'vendor': 'cisco',
            'type': 'init',
            'desc': '核心交换机初始化'
        },
        {
            'vendor': 'cisco',
            'type': 'vlan',
            'desc': '接入交换机VLAN配置'
        },
        {
            'vendor': 'huawei',
            'type': 'ospf',
            'desc': '汇聚路由器OSPF配置'
        },
        {
            'vendor': 'cisco',
            'type': 'acl',
            'desc': '边界防火墙ACL'
        }
    ]
    
    # 也可以让用户自定义
    print("使用默认配置列表还是自定义？")
    print("1. 使用默认（上述4个配置）")
    print("2. 自定义")
    choice = input("选择 (1/2): ")
    
    if choice == '2':
        config_requests = []
        print("\n请输入配置需求（输入空行结束）：")
        while True:
            desc = input("描述: ")
            if not desc:
                break
            vendor = input("厂商: ")
            config_type = input("类型: ")
            config_requests.append({
                'vendor': vendor,
                'type': config_type,
                'desc': desc
            })
    
    if not config_requests:
        print("没有配置需求")
        return
    
    # 显示将要生成的配置
    print(f"\n将生成 {len(config_requests)} 个配置：")
    for idx, req in enumerate(config_requests, 1):
        print(f"  {idx}. {req['desc']} ({req['vendor']} - {req['type']})")
    
    confirm = input("\n确认开始？(y/n): ")
    if confirm.lower() != 'y':
        return
    
    # 执行批量生成
    processor = BatchProcessor()
    results = processor.batch_generate_configs(config_requests)
    
    # 保存结果
    output_dir = processor.save_batch_results(results)
    
    print(f"\n{'='*60}")
    print(f"✓ 批量处理完成！")
    print(f"输出目录: {output_dir}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()