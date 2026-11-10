
import unittest

from chunking import chunk_document


class TestChunkDocument(unittest.TestCase):

    def test_empty_document(self):
        """An empty document should produce no chunks."""

        result = chunk_document([])

        self.assertEqual(result, [])

    def test_blank_pages(self):
        """Pages without readable words should be skipped."""

        result = chunk_document(["", "   ", "\n"])

        self.assertEqual(result, [])

    def test_short_document(self):
        """A short document should produce one chunk."""

        pages = ["Hello this is a test document"]

        result = chunk_document(pages)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["page_number"], 1)
        self.assertEqual(result[0]["word_count"], 6)

    def test_page_numbers(self):
        """Chunks should retain their original PDF page numbers."""

        pages = [
            "This is the first page",
            "This is the second page"
        ]

        result = chunk_document(pages)

        self.assertEqual(result[0]["page_number"], 1)
        self.assertEqual(result[1]["page_number"], 2)

    def test_chunk_overlap(self):
        """Consecutive chunks should share overlapping words."""

        pages = [
            "one two three four five six seven eight"
        ]

        result = chunk_document(
            pages,
            chunk_size=5,
            chunk_overlap=2
        )

        self.assertEqual(len(result), 2)

        first_chunk = result[0]["text"].split()
        second_chunk = result[1]["text"].split()

        self.assertEqual(
            first_chunk[-2:],
            second_chunk[:2]
        )


if __name__ == "__main__":
    unittest.main()
