import os
import sys
import io
import requests
from dotenv import load_dotenv

# 解决终端编码抖动，防止 UnicodeDecodeError
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def call_claude_api():
    # 1. 确定 API 端点 (Endpoint)
    url = "https://api.anthropic.com/v1/messages"
    
    # 2. 构造 Headers (协议头)
    headers = {
        "x-api-key": os.getenv("ANTHROPIC_API_KEY"), # 认证令牌
        "anthropic-version": "2023-06-01",           # API 版本声明
        "content-type": "application/json"           # 载荷格式
    }
    
    # 3. 构造 Body (载荷)
    # 模拟有记忆的对话结构
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 512,
        "messages": [
            {"role": "user", "content": "你好，我是网络工程师王威。"}, # 历史记录
            {"role": "assistant", "content": "你好，王威！很高兴见到你。"}, # AI 的历史回复
            {"role": "user", "content": "请问我刚才说我叫什么名字？"} # 之后的新问题
        ]
    }

    print("--- 发起 API 请求 ---")
    try:
        # 使用 json= 参数会自动设置 content-type 并在后台处理字典转 JSON 的逻辑
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        # 4. 获取响应状态码
        print(f"状态码: {response.status_code}") # 200 表示链路全通
        
        if response.status_code == 200:
            # 5. 解析并打印 JSON 回复
            data = response.json()
            print(f"Claude 回复: {data['content'][0]['text']}")
        else:
            # 如果依然报错，这里会打印出服务器返回的真实错误 JSON
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"网络异常: {e}")

if __name__ == "__main__":
    call_claude_api()