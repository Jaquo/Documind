
import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function Chat() {

  // Store the user's current question
  const [question, setQuestion] = useState("");

  // Store the conversation history
  const [messages, setMessages] = useState([]);

  // Track whether the AI is generating an answer
  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  async function handleAsk(event) {
    event.preventDefault();

    const userQuestion = question.trim();

    if (!userQuestion || loading) return;

    // Display the user's message
    setMessages(previous => [
      ...previous,
      {
        role: "user",
        content: userQuestion
      }
    ]);

    setQuestion("");
    setLoading(true);
    setError("");

    try {

      // Send the question to our FastAPI backend
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          question: userQuestion,
          top_k: 3
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to generate answer.");
      }

      // Add the AI response to the conversation
      setMessages(previous => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || []
        }
      ]);

    } catch (err) {
      setError(err.message);

    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel chat-panel">

      <h2>Chat with your document</h2>

      <div className="chat-messages">

        {messages.length === 0 && (
          <p className="chat-placeholder">
            Ask a question about your uploaded PDF.
          </p>
        )}

        {messages.map((message, index) => (

          <div
            key={index}
            className={`chat-message ${message.role}`}
          >

            <p>{message.content}</p>

            {message.sources && message.sources.length > 0 && (
              <details className="chat-sources">
                <summary>
                  View sources ({message.sources.length})
                </summary>

                {message.sources.map((source, i) => (
                  <div className="source" key={i}>
                    <strong>
                      {source.reference} Page {source.page_number}
                    </strong>
                    <p>{source.text}</p>
                  </div>
                ))}

              </details>
            )}

          </div>

        ))}

        {loading && (
          <p className="chat-placeholder" role="status">
            DocuMind is generating an answer...
          </p>
        )}

      </div>

      {error && <p className="error" role="alert">{error}</p>}

      <form className="chat-form" onSubmit={handleAsk}>

        <input
          type="text"
          value={question}
          onChange={event => setQuestion(event.target.value)}
          placeholder="Ask a question about your PDF..."
          aria-label="Question about the document"
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
        >
          {loading ? "Thinking..." : "Send"}
        </button>

      </form>

    </section>
  );
}

export default Chat;
