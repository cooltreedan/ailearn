import paho.mqtt.client as mqtt
import json
import ssl

# --- 配置你的设备信息 ---
PRINTER_IP = "192.168.250.169"  # 替换为你的打印机 IP
ACCESS_CODE = "024892e8"     # 替换为你的 8 位访问码
SERIAL_NUM = "22E8AJ582301663" # 替换为你的打印机序列号


# 1. 明确使用 VERSION2
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def on_connect(client, userdata, flags, rc, properties):
    # rc=0 表示认证和连接都成功了
    if rc == 0:
        print("✅ 成功连接到打印机！正在监听数据包...")
        # 就像开启端口镜像一样，订阅报告主题
        client.subscribe(f"device/{SERIAL_NUM}/report")
    else:
        print(f"❌ 连接失败，返回码: {rc} (检查 Access Code 是否正确)")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # 打印机发回的数据非常多，我们只提取关心的部分
        if 'print' in payload:
            data = payload['print']
            nozzle_temp = data.get('nozzle_temper')
            bed_temp = data.get('bed_temper')
            percent = data.get('mc_percent')
            
            # 只有在有数据时才打印，避免刷屏
            if nozzle_temp is not None:
                print(f"Nozzle 喷嘴: {nozzle_temp}℃ | 热床: {bed_temp}℃ | 进度: {percent}%")
    except Exception as e:
        print(f"解析 JSON 出错: {e}")

# 2. 身份验证：用户名固定为 'bblp'，密码是 Access Code
client.username_pw_set("bblp", ACCESS_CODE)

# 3. 安全设置：Bambu 使用自签名证书，所以我们要“放行”
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True) 

client.on_connect = on_connect
client.on_message = on_message

print(f"正在尝试建立 MQTT 连接 {PRINTER_IP}:8883...")
try:
    client.connect(PRINTER_IP, 8883, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\n用户停止监控。")
except Exception as e:
    print(f"发生异常: {e}")