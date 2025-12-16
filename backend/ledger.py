# ledger.py
import json
import os

LEDGER_FILE = "storage/ledger.json"

os.makedirs("storage", exist_ok=True)

if not os.path.exists(LEDGER_FILE):
    with open(LEDGER_FILE, "w") as f:
        json.dump([], f)

def load_ledger():
    with open(LEDGER_FILE, "r") as f:
        return json.load(f)

def save_ledger(data):
    with open(LEDGER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_file(file_hash, filename, chunks, chunk_hashes, merkle_root, signature):
    ledger = load_ledger()
    ledger.append({
        "hash": file_hash,
        "meta": {
            "filename": filename,
            "chunk_names": [c["name"] for c in chunks],
            "chunk_hashes": chunk_hashes,
            "merkle_root": merkle_root,
            "signature": signature.hex()
        }
    })
    save_ledger(ledger)


def get_file(file_hash):
    ledger = load_ledger()
    return next((f for f in ledger if f["hash"] == file_hash), None)

def get_summary():
    data = load_ledger()
    summary = []

    for entry in data:
        meta = entry["meta"]

        summary.append({
            "hash": entry["hash"],
            "filename": meta["filename"],
            "chunks": len(meta["chunk_names"]),
            "merkle_root": meta["merkle_root"],
            "signature": meta["signature"]
        })

    return summary
