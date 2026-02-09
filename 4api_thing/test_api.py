import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 测试Claude API
try:
    from anthropic import Anthropic
    
    client = Anthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Hello! 请用一句话介绍你自己"}
        ]
    )
    
    print("✓ API连接成功！")
    print(f"Claude回复: {message.content[0].text}")
    
except Exception as e:
    print(f"✗ 连接失败: {e}")