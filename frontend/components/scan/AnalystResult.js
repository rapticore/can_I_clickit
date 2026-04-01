"use client";

import { useState } from "react";
import Card from "components/ui/Card";
import Badge from "components/ui/Badge";

function threatBadgeVariant(level) {
  if (level === "dangerous") return "danger";
  if (level === "suspicious") return "warning";
  return "safe";
}

export default function AnalystResult({ result }) {
  const [showRaw, setShowRaw] = useState(false);

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-text-primary">Analysis Result</h2>
        <Badge variant={threatBadgeVariant(result.threat_level)}>
          {result.threat_level}
        </Badge>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-4">
        <div className="rounded-xl border border-card-edge bg-white p-3">
          <p className="text-xs text-text-muted mb-1">Confidence</p>
          <p className="font-semibold text-text-primary">
            {result.confidence} ({result.confidence_score}%)
          </p>
        </div>
        <div className="rounded-xl border border-card-edge bg-white p-3">
          <p className="text-xs text-text-muted mb-1">Analysis Tier</p>
          <p className="font-semibold text-text-primary">{result.analysis_tier}</p>
        </div>
        <div className="rounded-xl border border-card-edge bg-white p-3">
          <p className="text-xs text-text-muted mb-1">Latency</p>
          <p className="font-semibold text-text-primary">{result.latency_ms}ms</p>
        </div>
        <div className="rounded-xl border border-card-edge bg-white p-3">
          <p className="text-xs text-text-muted mb-1">Pattern</p>
          <p className="font-semibold text-text-primary">{result.scam_pattern || "None"}</p>
        </div>
      </div>

      <div className="rounded-xl border border-card-edge bg-white p-3 mb-4">
        <p className="text-xs text-text-muted mb-1">Summary</p>
        <p className="text-sm text-text-primary">{result.verdict_summary || "N/A"}</p>
      </div>

      {result.signals && result.signals.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-semibold text-text-primary mb-2">Signals</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-card-edge text-left text-text-muted">
                  <th className="pb-2 pr-4 font-medium">Source</th>
                  <th className="pb-2 pr-4 font-medium">Score</th>
                  <th className="pb-2 font-medium">Detail</th>
                </tr>
              </thead>
              <tbody>
                {result.signals.map((sig, i) => (
                  <tr key={i} className="border-b border-card-edge/50">
                    <td className="py-2 pr-4 font-mono text-xs">{sig.source}</td>
                    <td className="py-2 pr-4">{sig.score}</td>
                    <td className="py-2 text-text-muted">{sig.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <button
        onClick={() => setShowRaw(!showRaw)}
        className="text-sm font-semibold text-brand cursor-pointer hover:underline"
      >
        {showRaw ? "Hide" : "Show"} Raw JSON
      </button>
      {showRaw && (
        <pre className="mt-2 rounded-xl border border-card-edge bg-slate-900 text-slate-200 p-4 overflow-x-auto text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </Card>
  );
}
