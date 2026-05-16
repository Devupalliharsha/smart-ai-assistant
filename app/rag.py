"""
rag.py
"""
import os, json, re, uuid, math
from pathlib import Path

STORE_DIR = Path("./vector_store")
INDEX_FILE = STORE_DIR / "index.json"

def _load() -> list:
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    return []

def _save(data: list):
    STORE_DIR.mkdir(exist_ok=True)
    INDEX_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

def _tokenize(text: str) -> dict:
    """Simple TF bag-of-words vector."""
    words = re.findall(r"[a-z]+", text.lower())
    tf = {}
    for w in words:
        tf[w] = tf.get(w, 0) + 1
    return tf

def _cosine(a: dict, b: dict) -> float:
    keys = set(a) & set(b)
    dot  = sum(a[k] * b[k] for k in keys)
    na   = math.sqrt(sum(v*v for v in a.values()))
    nb   = math.sqrt(sum(v*v for v in b.values()))
    return dot / (na * nb + 1e-9)

def _chunk(text: str, size=500, overlap=50) -> list:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start+size].strip())
        start += size - overlap
    return [c for c in chunks if len(c) > 30]

def _extract(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in (".txt", ".md"):
        return content.decode("utf-8", errors="replace")
    if ext == ".pdf":
        import pdfplumber, io
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    raise ValueError(f"Unsupported: {ext}")

def ingest_document(content: bytes, filename: str) -> dict:
    text   = _extract(content, filename)
    chunks = _chunk(text)
    if not chunks:
        raise ValueError("No text found.")
    doc_id = str(uuid.uuid4())
    data   = _load()
    for i, chunk in enumerate(chunks):
        data.append({
            "id": f"{doc_id}__{i}",
            "doc_id": doc_id,
            "filename": filename,
            "text": chunk,
            "vec": _tokenize(chunk),
        })
    _save(data)
    return {"doc_id": doc_id, "chunks_stored": len(chunks), "filename": filename}

def retrieve_context(query: str, n: int = 3) -> str:
    data = _load()
    if not data:
        return ""
    qvec    = _tokenize(query)
    scored  = sorted(data, key=lambda d: _cosine(qvec, d["vec"]), reverse=True)
    top     = scored[:n]
    return "\n\n---\n\n".join(f"[From: {c['filename']}]\n{c['text']}" for c in top)

def list_documents() -> list:
    docs = {}
    for d in _load():
        did = d["doc_id"]
        if did not in docs:
            docs[did] = {"doc_id": did, "filename": d["filename"], "chunks": 0}
        docs[did]["chunks"] += 1
    return list(docs.values())

def delete_document(doc_id: str) -> int:
    data    = _load()
    kept    = [d for d in data if d["doc_id"] != doc_id]
    deleted = len(data) - len(kept)
    _save(kept)
    return deleted