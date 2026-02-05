ConfigGen/
│
├── main.py                # 项目入口，控制对话流
├── models/
│   └── topology.py        # 定义 JSON 数据结构和校验
├── utils/
│   ├── parser.py          # 处理用户文本输入，转化为结构化字典
│   └── renderer.py        # 调用 Pyvis 或 NetworkX 生成拓扑图
└── data/
    └── current_topo.json  # 存储当前生成的拓扑状态