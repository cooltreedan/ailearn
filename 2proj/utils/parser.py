import re

class InputParser:
    @staticmethod
    def parse_device_info(input_str):
        """
        解析格式: 'R1, Cisco, Router' 或 'FW1, PaloAlto, Firewall'
        """
        parts = [p.strip() for p in input_str.split(',')]
        if len(parts) == 3:
            return {"id": parts[0], "brand": parts[1].lower(), "type": parts[2].lower()}
        return None

    @staticmethod
    def parse_link_info(input_str):
        """
        使用正则匹配连接关系
        支持格式: 'R1:Gi0/0 连接 R2:Gi0/0' 或 'R1:G0/1 connect R2:G0/1'
        """
        pattern = r"([\w-]+):([\w/]+)\s+(?:连接|connect)\s+([\w-]+):([\w/]+)"
        match = re.search(pattern, input_str)
        if match:
            return {
                "source": f"{match.group(1)}:{match.group(2)}",
                "target": f"{match.group(3)}:{match.group(4)}",
                "network": "TBD" # 初始网段设为待定
            }
        return None