import os
import glob
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
from docx import Document
import fitz  # PyMuPDF for PDFs
import faiss

data_dir = "data"

# --- Read file functions ---
def read_txt(path):
    return Path(path).read_text(encoding="utf-8", errors="ignore")

def read_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def read_pdf(path):
    text = ""
    with fitz.open(path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

# --- Load documents ---
files = []
for ext in ["*.txt", "*.docx", "*.pdf"]:
    files.extend(glob.glob(os.path.join(data_dir, ext)))

if not files:
    raise FileNotFoundError(f"No reference documents found in '{data_dir}' folder.")

docs = []
metas = []
for file in files:
    ext = file.lower()
    if ext.endswith(".txt"):
        content = read_txt(file)
    elif ext.endswith(".docx"):
        content = read_docx(file)
    elif ext.endswith(".pdf"):
        content = read_pdf(file)
    else:
        continue
    docs.append(content)
    metas.append({"source": os.path.basename(file)})

print(f"Loaded {len(docs)} documents from {data_dir}")

# --- Chunking ---
def chunk_text(text, size=500):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

chunks = []
chunk_metas = []
for doc_text, meta in zip(docs, metas):
    split_chunks = chunk_text(doc_text)
    chunks.extend(split_chunks)
    chunk_metas.extend([meta] * len(split_chunks))

print(f"Total chunks: {len(chunks)}")

# --- Embeddings ---
model = SentenceTransformer("all-MiniLM-L6-v2")
embs = model.encode(chunks, show_progress_bar=True)

if embs.size == 0:
    raise ValueError("Embedding generation failed. No embeddings created.")

# --- Save FAISS index ---
dim = embs.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embs)
faiss.write_index(index, "faiss.index")

# --- Save chunks + metadata ---
with open("texts.pkl", "wb") as f:
    pickle.dump({"texts": chunks, "metadatas": chunk_metas}, f)

print("FAISS index saved to 'faiss.index'")
print("Texts + metadata saved to 'texts.pkl'")
