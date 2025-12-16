import hashlib

def hash_data(data: bytes):
    return hashlib.sha256(data).hexdigest()

def merkle_root(hashes):
    if len(hashes) == 1:
        return hashes[0]

    next_level = []
    for i in range(0, len(hashes), 2):
        left = hashes[i]
        right = hashes[i+1] if i+1 < len(hashes) else left
        next_level.append(
            hash_data((left + right).encode())
        )
    return merkle_root(next_level)
