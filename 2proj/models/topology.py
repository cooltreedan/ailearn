import json

class TopologyModel:
    def __init__(self, project_name):
        self.data = {
            "topology_name": project_name,
            "nodes": [],
            "links": []
        }

    def add_node(self, node_info):
        if node_info:
            self.data["nodes"].append(node_info)

    def add_link(self, link_info):
        if link_info:
            self.data["links"].append(link_info)

    def save_to_json(self, filename="data/current_topo.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)