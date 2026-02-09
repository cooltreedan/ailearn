import requests

def get_ip_info_chinese():
    target_ip = input("请输入你想查询的 IP 地址: ")
    url = f"http://ip-api.com/json/{target_ip}"
    # ... 剩下的逻辑不变
    
    # 定义查询参数，就像你在 Postman 的 Params 表格里填的一样
    query_params = {
        "lang": "zh-CN"  # 这里的 Key 和 Value 对应 Postman 里的设置
    }

    try:
        # 使用 params 关键字将字典传入
        response = requests.get(url, params=query_params)
        
        if response.status_code == 200:
            data = response.json()
            # 现在你会发现打印出来的国家和城市都是中文了
            print(f"国家: {data.get('country')}")
            print(f"城市: {data.get('city')}")
            print(f"运营商: {data.get('isp')}")
        else:
            print(f"请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    get_ip_info_chinese()