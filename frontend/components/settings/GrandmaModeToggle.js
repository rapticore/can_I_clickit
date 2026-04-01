"use client";

import { useUXMode } from "lib/ux-mode-context";
import Card from "components/ui/Card";

export default function GrandmaModeToggle() {
  const { isGrandmaMode, setIsGrandmaMode } = useUXMode();

  return (
    <Card>
      <h2 className="text-lg font-bold text-text-primary mb-4">Display Mode</h2>

      <div className="flex items-center gap-4">
        <button
          onClick={() => setIsGrandmaMode(true)}
          className={`flex-1 rounded-xl border-2 p-4 text-left cursor-pointer transition-all ${
            isGrandmaMode
              ? "border-brand bg-brand/5"
              : "border-card-edge hover:border-brand/30"
          }`}
        >
          <p className="text-lg font-semibold text-text-primary">Simple Mode</p>
          <p className="text-sm text-text-muted mt-1">
            Large text, clear verdicts, step-by-step guidance. Best for
            non-technical users.
          </p>
        </button>

        <button
          onClick={() => setIsGrandmaMode(false)}
          className={`flex-1 rounded-xl border-2 p-4 text-left cursor-pointer transition-all ${
            !isGrandmaMode
              ? "border-brand bg-brand/5"
              : "border-card-edge hover:border-brand/30"
          }`}
        >
          <p className="text-lg font-semibold text-text-primary">Expert Mode</p>
          <p className="text-sm text-text-muted mt-1">
            Signal tables, confidence scores, raw data, and technical details
            for analysts.
          </p>
        </button>
      </div>
    </Card>
  );
}
