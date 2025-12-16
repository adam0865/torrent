from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, shutil, tempfile, json

from torrent import split_file, rebuild_file, hash_file, hash_bytes
from merkle import merkle_root
from ledger import add_file, get_file, get_summary
from swarm import download_swarm
from crypto import sign

# =========================
# APP INIT (HARUS DULU)
# =========================
app = FastAPI()

# =========================
# CORS (SETELAH app ADA)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# PATH CONFIG
# =========================
BASE = os.path.join(os.path.dirname(__file__), "storage")
UPLOADS = os.path.join(BASE, "uploads")
CHUNKS = os.path.join(BASE, "chunks")
REBUILT = os.path.join(BASE, "rebuilt")
NODES_FILE = os.path.join(BASE, "nodes.json")

for d in [UPLOADS, CHUNKS, REBUILT]:
    os.makedirs(d, exist_ok=True)

os.makedirs(BASE, exist_ok=True)

# =========================
# UPLOAD
# =========================
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    upload_path = os.path.join(UPLOADS, file.filename)

    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_hash = hash_file(upload_path)
    chunk_dir = os.path.join(CHUNKS, file_hash)

    chunks, chunk_hashes = split_file(upload_path, chunk_dir)
    root = merkle_root(chunk_hashes)
    signature = sign(file_hash.encode())

    add_file(
        file_hash=file_hash,
        filename=file.filename,
        chunks=chunks,
        chunk_hashes=chunk_hashes,
        merkle_root=root,
        signature=signature
    )

    return {
        "hash": file_hash,
        "filename": file.filename,
        "chunks": len(chunks),
        "merkle_root": root
    }

# =========================
# DOWNLOAD (REBUILD)
# =========================
@app.get("/download/{file_hash}")
def download(file_hash: str):
    entry = get_file(file_hash)
    if not entry:
        raise HTTPException(404, "File not found in ledger")

    meta = entry["meta"]

    tmp = tempfile.mkdtemp()
    chunk_paths = download_swarm(file_hash, meta["chunk_names"], tmp)

    hashes = []
    for p in chunk_paths:
        with open(p, "rb") as f:
            hashes.append(hash_bytes(f.read()))

    if merkle_root(hashes) != meta["merkle_root"]:
        raise HTTPException(400, "Integrity check failed")

    output = os.path.join(REBUILT, meta["filename"])
    rebuild_file(
        [{"index": i, "path": p} for i, p in enumerate(chunk_paths)],
        output
    )

    return FileResponse(
        output,
        filename=meta["filename"],
        media_type="application/octet-stream"
    )

# =========================
# CHUNK ENDPOINT (JANGAN DIUBAH)
# =========================
@app.get("/chunk/{file_hash}/{chunk_name}")
def get_chunk(file_hash: str, chunk_name: str):
    path = f"storage/chunks/{file_hash}/{chunk_name}"
    if not os.path.exists(path):
        raise HTTPException(404)
    return FileResponse(path)

# =========================
# LEDGER SUMMARY
# =========================
@app.get("/summary")
def summary():
    return get_summary()

# =========================
# NODE REGISTRY
# =========================
@app.get("/nodes")
def get_nodes():
    if not os.path.exists(NODES_FILE):
        return []
    with open(NODES_FILE, "r") as f:
        return json.load(f)

@app.post("/register-node")
def register_node(node: dict):
    nodes = []

    if os.path.exists(NODES_FILE):
        with open(NODES_FILE, "r") as f:
            nodes = json.load(f)

    nodes.append(node)

    with open(NODES_FILE, "w") as f:
        json.dump(nodes, f, indent=2)

    return {"status": "ok"}
