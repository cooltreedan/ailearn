import requests

# 就像在网管平台查询特定设备信息
response = requests.get("https://jsonplaceholder.typicode.com/users/1")
user_data = response.json()

print(f"用户姓名: {user_data.get('name')}")
print(f"公司名称: {user_data.get('company').get('name')}")