
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from httpx import RequestError

from main import app


class TestAPI(unittest.TestCase):

    def setUp(self):
        # Create a fake vector store for testing.
        # This avoids loading the real embedding model.
        self.store = Mock()
        self.store.index = None

        app.state.vector_store = self.store

        # Without a context manager, TestClient does
        # not run the application's startup lifespan.
        self.client = TestClient(app)

    def test_home_endpoint(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["status"],
            "running"
        )

    def test_reject_non_pdf(self):
        response = self.client.post(
            "/upload",
            files={
                "file": (
                    "notes.txt",
                    b"Hello world",
                    "text/plain"
                )
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_reject_fake_pdf(self):
        response = self.client.post(
            "/upload",
            files={
                "file": (
                    "fake.pdf",
                    b"This is not a PDF",
                    "application/pdf"
                )
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_reject_oversized_pdf(self):
        response = self.client.post(
            "/upload",
            files={
                "file": (
                    "large.pdf",
                    b"%PDF-" + b"x" * (10 * 1024 * 1024),
                    "application/pdf"
                )
            }
        )

        self.assertEqual(response.status_code, 413)

    def test_search_without_document(self):
        response = self.client.post(
            "/search",
            json={"question": "What is cybersecurity?"}
        )

        self.assertEqual(response.status_code, 404)

    def test_ask_without_document(self):
        response = self.client.post(
            "/ask",
            json={"question": "What is cybersecurity?"}
        )

        self.assertEqual(response.status_code, 404)

    def test_reject_invalid_top_k(self):
        response = self.client.post(
            "/ask",
            json={
                "question": "What is cybersecurity?",
                "top_k": 100
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_empty_question(self):
        # Simulate an indexed document.
        self.store.index = object()

        response = self.client.post(
            "/ask",
            json={"question": "   "}
        )

        self.assertEqual(response.status_code, 400)

    def test_ollama_unavailable(self):
        # Simulate an indexed document and search results.
        self.store.index = object()
        self.store.search.return_value = [
            {
                "page_number": 1,
                "text": "Keep software updated.",
                "similarity_score": 0.9
            }
        ]

        # Simulate a connection failure from Ollama.
        with patch(
            "main.generate_answer",
            side_effect=RequestError("Connection failed")
        ):
            response = self.client.post(
                "/ask",
                json={"question": "Why update software?"}
            )

        self.assertEqual(response.status_code, 503)

    def test_ask_returns_sources(self):
        self.store.index = object()
        self.store.search.return_value = [
            {
                "page_number": 8,
                "text": "Updates patch vulnerabilities.",
                "similarity_score": 0.9
            }
        ]

        with patch(
            "main.generate_answer",
            return_value="Updates fix security issues [1]."
        ):
            response = self.client.post(
                "/ask",
                json={"question": "Why update software?"}
            )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("[1]", data["answer"])
        self.assertEqual(
            data["sources"][0]["page_number"],
            8
        )
        self.assertEqual(
            data["sources"][0]["reference"],
            "[1]"
        )


if __name__ == "__main__":
    unittest.main()
