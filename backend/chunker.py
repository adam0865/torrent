import os

def split_file(file_path, out_dir, chunk_size=1024*1024):
    os.makedirs(out_dir, exist_ok=True)
    chunks = []

    with open(file_path, "rb") as f:
        i = 0
        while True:
            data = f.read(chunk_size)
            if not data:
                break

            chunk_path = os.path.join(out_dir, f"{i:04d}.chunk")
            with open(chunk_path, "wb") as c:
                c.write(data)

            chunks.append(chunk_path)
            i += 1

    return chunks


def rebuild_file(chunks, output_path):
    with open(output_path, "wb") as out:
        for chunk in sorted(chunks):
            with open(chunk, "rb") as c:
                out.write(c.read())
