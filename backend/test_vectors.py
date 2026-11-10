
import sys
import pymupdf

from chunking import chunk_document
from vector_store import LocalVectorStore


# Get the PDF filename from the command line
if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python test_vectors.py path/to/document.pdf"
    )

pdf_path = sys.argv[1]

# Extract text from the PDF
with pymupdf.open(pdf_path) as document:
    pages = [page.get_text() for page in document]

# Split the extracted text into chunks
chunks = chunk_document(pages)

print(f"Created {len(chunks)} document chunks.")

# Build the vector database
vector_store = LocalVectorStore()

total = vector_store.build_index(chunks)

print(f"Stored {total} vectors in FAISS.")
print(f"Embedding dimensions: {vector_store.index.d}")

# Test a semantic search
question = "Why should businesses regularly update their software?"

print(f"\nQuestion: {question}")

results = vector_store.search(question, top_k=3)

for result in results:

    print("\n----------------------------")
    print(f"Page: {result['page_number']}")
    print(f"Similarity: {result['similarity_score']:.3f}")
    print(f"Text: {result['text'][:400]}")
