import { useEffect, useState } from "react";
import "./App.css";
import Chat from "./Chat";

const API_URL = "http://127.0.0.1:8000";

function App() {

  // Store information about the application
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [selectedFile, setSelectedFile] = useState(null);
  const [document, setDocument] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  // Check whether FastAPI is running
  useEffect(() => {
    fetch(`${API_URL}/`)
      .then(response => {
        if (!response.ok) throw new Error("Backend error");
        return response.json();
      })
      .then(data => setBackendStatus(data.status))
      .catch(() => setBackendStatus("Unavailable"));
  }, []);

  // Handle selecting a PDF
  function handleFileChange(event) {
    const file = event.target.files[0];

    setSelectedFile(file || null);
    setDocument(null);
    setError("");
  }

  // Upload the selected PDF to FastAPI
  async function handleUpload(event) {
    event.preventDefault();

    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF file.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("The PDF must be smaller than 10 MB.");
      return;
    }

    setUploading(true);
    setError("");

    // Create the form data sent to FastAPI
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      // Store the information returned by FastAPI
      setDocument(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <main className="app">

      <header className="header">
        <div>
          <h1>DocuMind</h1>
          <p>Your local AI document assistant</p>
        </div>

        <span className="status">
          Backend: {backendStatus}
        </span>
      </header>

      <section className="panel">

        <h2>Upload a document</h2>
        <p>Select a PDF to analyse with DocuMind.</p>

        <form onSubmit={handleUpload}>

          <div className="upload-area">
            <label htmlFor="pdf-upload">
              Choose a PDF document
            </label>

            <input
              id="pdf-upload"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
            />
          </div>

          {selectedFile && (
            <p className="selected-file">
              Selected: {selectedFile.name}
            </p>
          )}

          <button
            type="submit"
            disabled={!selectedFile || uploading}
          >
            {uploading ? "Processing PDF..." : "Upload PDF"}
          </button>

        </form>

        {error && <p className="error" role="alert">{error}</p>}

      </section>

      {document && (
        <section className="panel results">

          <h2>Document processed successfully!</h2>

          <p><strong>Filename:</strong> {document.filename}</p>
          <p><strong>Pages:</strong> {document.page_count}</p>
          <p>
            <strong>Characters extracted:</strong>{" "}
            {document.characters_extracted}
          </p>
          <p>
            <strong>Chunks generated:</strong>{" "}
            {document.total_chunks}
          </p>

          <h3>Extracted text previews</h3>

          {document.chunks_preview.map(chunk => (
            <div className="chunk" key={chunk.chunk_id}>
              <strong>Page {chunk.page_number}</strong>
              <p>{chunk.preview}...</p>
            </div>
          ))}

        </section>
      )}


      {/* Show the chat after a PDF has been uploaded */}
      {document && <Chat />}

    </main>
  );
}

export default App;
