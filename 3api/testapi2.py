import requests

new_post = {
    "title": "网工实验帖子",
    "body": "这是一条测试 BGP 配置的模拟数据",
    "userId": 1
}
response = requests.post("https://jsonplaceholder.typicode.com/posts", json=new_post)
print(f"模拟创建成功，服务器返回 ID: {response.json().get('id')}") # 通常会返回 101