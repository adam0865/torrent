# swarm.py
import os
import shutil
from nodes import pick_nodes

def download_swarm(file_hash, chunk_names, target_dir):
    downloaded = []

    try:
        nodes = pick_nodes()
    except Exception:
        nodes = []

    # 🔁 FALLBACK: local storage (single-node mode)
    if not nodes:
        local_dir = f"storage/chunks/{file_hash}"
        if not os.path.exists(local_dir):
            raise Exception("No nodes and no local chunks")

        for name in chunk_names:
            src = os.path.join(local_dir, name)
            dst = os.path.join(target_dir, name)
            shutil.copyfile(src, dst)
            downloaded.append(dst)

        return downloaded

    # 🌐 REAL SWARM MODE
    for node in nodes:
        for name in chunk_names:
            # placeholder real P2P fetch
            pass

    return downloaded
