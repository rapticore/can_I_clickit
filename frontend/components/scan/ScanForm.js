"use client";

import { useState } from "react";
import { useUXMode } from "lib/ux-mode-context";
import Button from "components/ui/Button";
import Input from "components/ui/Input";

const quickSamples = [
  {
    label: "Phishing sample",
    content:
      "URGENT: Your account was suspended. Verify immediately at https://secure-account-review-now.xyz",
  },
  {
    label: "Benign sample",
    content: "Hey, are we still meeting for coffee tomorrow at 9am?",
  },
];

export default function ScanForm({ onSubmit, loading }) {
  const { isGrandmaMode } = useUXMode();
  const [scanType, setScanType] = useState("text");
  const [content, setContent] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!content.trim()) return;

    // Auto-detect scan type in grandma mode
    let type = scanType;
    if (isGrandmaMode) {
      try {
        new URL(content.trim());
        type = "url";
      } catch {
        type = "text";
      }
    }

    onSubmit(type, content.trim());
  }

  if (isGrandmaMode) {
    return (
      <form onSubmit={handleSubmit} className="grid gap-4">
        <label className="text-lg font-semibold text-text-primary">
          Is something suspicious? Paste it here.
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={6}
          placeholder="Paste the suspicious message, email, or link here..."
          className="w-full rounded-xl border border-card-edge px-4 py-3 text-lg text-text-primary bg-white focus:outline-none focus:ring-2 focus:ring-brand/40 resize-y min-h-[140px]"
        />

        <div className="flex flex-wrap gap-2">
          {quickSamples.map((sample) => (
            <button
              key={sample.label}
              type="button"
              onClick={() => setContent(sample.content)}
              className="rounded-full border border-card-edge bg-bg-base px-4 py-2 text-sm text-text-muted hover:bg-card transition-colors cursor-pointer"
            >
              {sample.label}
            </button>
          ))}
        </div>

        <Button type="submit" size="lg" loading={loading} className="w-full text-lg">
          Check This For Me
        </Button>
      </form>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-4">
      <div className="grid gap-4 sm:grid-cols-[1fr_auto]">
        <Input
          label="Content to analyze"
          type="textarea"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste suspicious message or URL here..."
          rows={5}
        />
        <div className="grid gap-3 content-start">
          <div className="grid gap-1.5">
            <label className="text-sm font-medium text-text-muted" htmlFor="scan-type">
              Scan Type
            </label>
            <select
              id="scan-type"
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
              className="rounded-xl border border-card-edge bg-white px-3 py-2.5 text-text-primary focus:outline-none focus:ring-2 focus:ring-brand/40"
            >
              <option value="text">Text</option>
              <option value="url">URL</option>
              <option value="email">Email</option>
              <option value="sms">SMS</option>
            </select>
          </div>
          <div className="flex flex-wrap gap-2">
            {quickSamples.map((sample) => (
              <button
                key={sample.label}
                type="button"
                onClick={() => setContent(sample.content)}
                className="rounded-full border border-card-edge bg-bg-base px-3 py-1.5 text-xs text-text-muted hover:bg-card transition-colors cursor-pointer"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <Button type="submit" loading={loading}>
        Analyze
      </Button>
    </form>
  );
}
