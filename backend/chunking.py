
def chunk_document(pages, chunk_size=200, chunk_overlap=40):

    chunks = []

    # Process each page separately
    for page_number, page_text in enumerate(pages, start=1):

        words = page_text.split()

        start = 0
        chunk_index = 1

        while start < len(words):

            # Calculate where this chunk ends
            end = min(start + chunk_size, len(words))

            # Extract words and combine them into text
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            # Store the chunk and its metadata
            chunks.append({
                "chunk_id": f"page-{page_number}-chunk-{chunk_index}",
                "page_number": page_number,
                "text": chunk_text,
                "word_count": len(chunk_words)
            })

            # Stop when we reach the end of the page
            if end == len(words):
                break

            # Move forward, leaving an overlap
            start = end - chunk_overlap
            chunk_index += 1

    return chunks
