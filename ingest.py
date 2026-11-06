from pathlib import Path
import chromadb

KB_DIR = Path("knowledge_base")
DB_DIR = "chroma_db"


def chunk_file(path):
    """Split one markdown file into one chunk per '## ' section."""
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].lstrip("# ").strip()
    chunks = []
    for part in text.replace("\r\n", "\n").split("\n## ")[1:]:
        heading, _, body = part.partition("\n")
        heading = heading.strip()
        chunks.append({
            "id": f"{path.stem}::{heading}",
            "text": f"{title} - {heading}\n{body.strip()}",
            "meta": {"source": path.name, "title": title, "section": heading},
        })
    return chunks


def main():
    client = chromadb.PersistentClient(path=DB_DIR)
    try:
        client.delete_collection("security_kb")
    except Exception:
        pass
    collection = client.create_collection("security_kb")

    files = sorted(KB_DIR.glob("*.md"))
    chunks = []
    for path in files:
        chunks.extend(chunk_file(path))

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["meta"] for c in chunks],
    )
    print(f"Indexed {len(chunks)} chunks from {len(files)} files")


if __name__ == "__main__":
    main()
