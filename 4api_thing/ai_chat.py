import os
from dotenv import load_dotenv
from anthropic import Anthropic

# 加载API密钥
load_dotenv()

def chat_with_ai(user_message):
    """
    与AI对话的函数
    
    参数:
        user_message: 用户的消息
    返回:
        AI的回复
    """
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # 提取AI的回复文本
        return message.content[0].text
        
    except Exception as e:
        return f"错误: {e}"

def main():
    """主程序"""
    print("=== AI对话助手 ===")
    print("输入 'quit' 退出\n")
    
    while True:
        user_input = input("您: ")
        
        if user_input.lower() == 'quit':
            print("再见！")
            break
        
        if not user_input.strip():
            continue
        
        print("\nAI正在思考...\n")
        response = chat_with_ai(user_input)
        print(f"AI: {response}\n")
        print("-" * 50)

if __name__ == "__main__":
    main()