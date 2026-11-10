
import faiss
import numpy as np
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer


class LocalVectorStore:

    def __init__(self): #constructor

        # Load our local embedding model
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device="cpu"
        )

        self.index = None
        self.chunks = []


    def build_index(self, chunks): #method to build a FAISS index from the provided document chunks.

        # Store our document chunks
        self.chunks = [
            chunk for chunk in chunks
            if chunk["text"].strip()
        ]

        if not self.chunks:
            raise ValueError("No chunks to embed.")

        # Get the text from each chunk
        texts = [chunk["text"] for chunk in self.chunks]

        # Convert text into numerical vectors
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        # FAISS expects float32 vectors because it is optimized for performance and memory usage. The np.ascontiguousarray function ensures that the embeddings are stored in a contiguous block of memory, which is required by FAISS for efficient processing.
        vectors = np.ascontiguousarray(
            embeddings,
            dtype=np.float32
        )

        # Create a FAISS index
        dimensions = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dimensions)

        # Store our embeddings
        self.index.add(vectors)

        return self.index.ntotal


    def search(self, question, top_k=3):

        if self.index is None:
            raise ValueError("Build the index first.")

        if not question.strip():
            raise ValueError("Question cannot be empty.")

        # Convert the question into an embedding
        query_embedding = self.model.encode(
            [question],
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        query_vector = np.ascontiguousarray(
            query_embedding,
            dtype=np.float32
        )

        # Search for the nearest vectors
        scores, indices = self.index.search(
            query_vector,
            min(top_k, self.index.ntotal)
        )

        results = []

        for index, score in zip(indices[0], scores[0]):

            if index < 0:
                continue

            chunk = self.chunks[index]

            results.append({
                "page_number": chunk["page_number"],
                "text": chunk["text"],
                "similarity_score": float(score)
            })

        return results


    def save(self, folder):
        # Check that the index exists
        if self.index is None:
            raise ValueError("No index to save.")

        # Create the directory if it doesn't exist
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        # Save the FAISS index
        faiss.write_index(
            self.index,
            str(folder / "index.faiss")
        )

        # Save the original document chunks
        with open(folder / "chunks.json", "w", encoding="utf-8") as file:
            json.dump(self.chunks, file, indent=2, ensure_ascii=False)


    def load(self, folder):
        folder = Path(folder)

        # Load the original document chunks
        with open(folder / "chunks.json", "r", encoding="utf-8") as file:
            chunks = json.load(file)

        # Load the FAISS index
        index = faiss.read_index(
            str(folder / "index.faiss")
        )

        # Check that the data matches
        if index.ntotal != len(chunks):
            raise ValueError("Index and chunks do not match.")

        # Restore our stored data
        self.chunks = chunks
        self.index = index


