"use client";

import { useState } from "react";
import { useUXMode } from "lib/ux-mode-context";
import { scans } from "lib/api";
import Card from "components/ui/Card";
import ScanForm from "components/scan/ScanForm";
import ScanResult from "components/scan/ScanResult";

export default function DashboardPage() {
  const { isGrandmaMode } = useUXMode();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleScan(scanType, content) {
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const data = await scans.analyze(scanType, content);
      setResult(data);
    } catch (err) {
      if (err.status === 429) {
        setError(
          isGrandmaMode
            ? "You've used all your free checks for today. Try again tomorrow!"
            : err.detail || "Rate limit exceeded. Upgrade for unlimited scans."
        );
      } else {
        setError(err.detail || err.message || "Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6">
      <div>
        <h1 className={`font-bold text-text-primary ${isGrandmaMode ? "text-3xl" : "text-2xl"}`}>
          {isGrandmaMode ? "Is it safe?" : "Threat Analysis"}
        </h1>
        <p className={`text-text-muted mt-1 ${isGrandmaMode ? "text-lg" : "text-sm"}`}>
          {isGrandmaMode
            ? "Paste anything suspicious and we'll check it for you."
            : "Submit suspicious text or links for AI-powered analysis."}
        </p>
      </div>

      <Card>
        <ScanForm onSubmit={handleScan} loading={loading} />
      </Card>

      {error && (
        <div className="rounded-xl border border-danger/30 bg-red-50 p-4">
          <p className="text-danger font-medium">{error}</p>
        </div>
      )}

      {result && <ScanResult result={result} />}
    </div>
  );
}
