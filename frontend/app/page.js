"use client";

import { useMemo, useState } from "react";

const defaultApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8880";
const defaultApiKey = process.env.NEXT_PUBLIC_API_KEY || "";

function pillClass(threatLevel) {
  switch (threatLevel) {
    case "dangerous":
      return "pill pill-danger";
    case "suspicious":
      return "pill pill-warning";
    case "safe":
      return "pill pill-safe";
    default:
      return "pill";
  }
}

export default function HomePage() {
  const [apiBaseUrl, setApiBaseUrl] = useState(defaultApiBaseUrl);
  const [apiKey, setApiKey] = useState(defaultApiKey);
  const [scanType, setScanType] = useState("text");
  const [content, setContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const prettyResult = useMemo(() => {
    if (!result) return "";
    return JSON.stringify(result, null, 2);
  }, [result]);

  async function submitScan(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!content.trim()) {
      setError("Enter a message or URL before running analysis.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/v1/scan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(apiKey ? { "X-API-Key": apiKey } : {}),
        },
        body: JSON.stringify({
          scan_type: scanType,
          content: content.trim(),
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `Request failed (${response.status})`);
      }
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to complete request.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <h1>Can I Click It? Local Test Console</h1>
        <p>Submit suspicious text or links and inspect the full API verdict payload.</p>
      </section>

      <section className="panel">
        <form className="scan-form" onSubmit={submitScan}>
          <div className="field-grid">
            <label>
              API Base URL
              <input
                type="url"
                value={apiBaseUrl}
                onChange={(e) => setApiBaseUrl(e.target.value)}
                placeholder="http://localhost:8880"
                required
              />
            </label>

            <label>
              API Key (optional if backend runs in dev-mode)
              <input
                type="text"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="dev-key-12345"
              />
            </label>

            <label>
              Scan Type
              <select value={scanType} onChange={(e) => setScanType(e.target.value)}>
                <option value="text">Text</option>
                <option value="url">URL</option>
              </select>
            </label>
          </div>

          <label className="message-field">
            Message / URL to analyze
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={8}
              placeholder="Paste suspicious message or URL here..."
            />
          </label>

          <div className="quick-fill">
            <button
              type="button"
              onClick={() =>
                setContent(
                  "URGENT: Your account was suspended. Verify immediately at https://secure-account-review-now.xyz"
                )
              }
            >
              Load phishing sample
            </button>
            <button
              type="button"
              onClick={() => setContent("Hey, are we still meeting for coffee tomorrow at 9am?")}
            >
              Load benign sample
            </button>
          </div>

          <button className="submit" type="submit" disabled={isLoading}>
            {isLoading ? "Analyzing..." : "Analyze"}
          </button>
        </form>
      </section>

      {error ? <p className="error">{error}</p> : null}

      {result ? (
        <section className="result">
          <div className="result-header">
            <h2>Analysis Result</h2>
            <span className={pillClass(result.threat_level)}>{result.threat_level}</span>
          </div>
          <div className="result-grid">
            <article>
              <h3>Summary</h3>
              <p>{result.verdict_summary || "No summary provided."}</p>
            </article>
            <article>
              <h3>Confidence</h3>
              <p>
                {result.confidence} ({result.confidence_score}%)
              </p>
            </article>
            <article>
              <h3>Consequence Warning</h3>
              <p>{result.consequence_warning || "N/A"}</p>
            </article>
            <article>
              <h3>Safe Action</h3>
              <p>{result.safe_action_suggestion || "N/A"}</p>
            </article>
          </div>
          <details>
            <summary>Raw JSON</summary>
            <pre>{prettyResult}</pre>
          </details>
        </section>
      ) : null}
    </main>
  );
}
