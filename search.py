import sys
import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("security_kb")

query = " ".join(sys.argv[1:])
results = collection.query(query_texts=[query], n_results=4)

for doc, meta, dist in zip(
    results["documents"][0], results["metadatas"][0], results["distances"][0]
):
    print(f"[{dist:.3f}] {meta['source']} > {meta['section']}")
    print("   " + doc.replace("\n", " ")[:160] + "...\n")
