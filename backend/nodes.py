import json
import os
import random

NODES_FILE = "nodes.json"

# init file
if not os.path.exists(NODES_FILE):
    with open(NODES_FILE, "w") as f:
        json.dump({"nodes": []}, f)


def register_node(address: str):
    with open(NODES_FILE) as f:
        data = json.load(f)

    if address not in data["nodes"]:
        data["nodes"].append(address)

        with open(NODES_FILE, "w") as f:
            json.dump(data, f, indent=2)

    return {
        "status": "registered",
        "nodes": data["nodes"]
    }


def get_nodes():
    with open(NODES_FILE) as f:
        return json.load(f)["nodes"]


def pick_nodes(k: int = 3):
    """
    Ambil node secara random untuk swarm download
    """
    nodes = get_nodes()
    if not nodes:
        raise Exception("No nodes available")

    random.shuffle(nodes)
    return nodes[:k]
