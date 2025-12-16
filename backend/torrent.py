import os
import hashlib

CHUNK_SIZE = 256 * 1024  # 256 KB

def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            h.update(block)
    return h.hexdigest()

def split_file(path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    chunks = []
    hashes = []

    with open(path, "rb") as f:
        i = 0
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break

            name = f"chunk_{i}"
            p = os.path.join(out_dir, name)

            with open(p, "wb") as c:
                c.write(data)

            h = hash_bytes(data)
            chunks.append({
                "index": i,
                "name": name,
                "path": p,
                "hash": h
            })
            hashes.append(h)
            i += 1

    return chunks, hashes



def rebuild_file(chunks, output):
    with open(output, "wb") as out:
        for c in sorted(chunks, key=lambda x: x["index"]):
            with open(c["path"], "rb") as f:
                out.write(f.read())
