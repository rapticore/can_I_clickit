"use client";

import { useState } from "react";
import { useUXMode } from "lib/ux-mode-context";
import TriageWizard from "components/recovery/TriageWizard";
import RecoveryChecklist from "components/recovery/RecoveryChecklist";

export default function RecoveryPage() {
  const { isGrandmaMode } = useUXMode();
  const [checklist, setChecklist] = useState(null);

  return (
    <div className="grid gap-6">
      <div>
        <h1 className={`font-bold text-text-primary ${isGrandmaMode ? "text-3xl" : "text-2xl"}`}>
          {isGrandmaMode ? "I think I was scammed" : "Incident Recovery"}
        </h1>
        <p className={`text-text-muted mt-1 ${isGrandmaMode ? "text-lg" : "text-sm"}`}>
          {isGrandmaMode
            ? "Answer a few questions and we'll tell you exactly what to do."
            : "Classify the incident and get a step-by-step recovery checklist."}
        </p>
      </div>

      {checklist ? (
        <div className="grid gap-4">
          <RecoveryChecklist checklist={checklist} />
          <button
            onClick={() => setChecklist(null)}
            className="text-sm text-brand hover:underline cursor-pointer"
          >
            Start over
          </button>
        </div>
      ) : (
        <TriageWizard onComplete={setChecklist} />
      )}
    </div>
  );
}
