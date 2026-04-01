"use client";

import { useState } from "react";
import { useUXMode } from "lib/ux-mode-context";
import Card from "components/ui/Card";
import Button from "components/ui/Button";

export default function RecoveryChecklist({ checklist }) {
  const { isGrandmaMode } = useUXMode();
  const steps = checklist.steps || [];
  const [completed, setCompleted] = useState(new Set());
  const [currentStep, setCurrentStep] = useState(0);

  function toggleStep(index) {
    setCompleted((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  }

  // Grandma mode: one step at a time
  if (isGrandmaMode) {
    const step = steps[currentStep];
    if (!step) return null;

    return (
      <Card>
        <p className="text-sm text-text-muted mb-2">
          Step {currentStep + 1} of {steps.length}
        </p>
        <h3 className="text-xl font-semibold text-text-primary mb-2">
          {step.title}
        </h3>
        <p className="text-lg text-text-muted mb-6">{step.description}</p>

        {step.action_url && (
          <a
            href={step.action_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block mb-4 rounded-lg bg-brand/10 px-4 py-2 text-brand font-medium"
          >
            {step.action_label || "Open Link"}
          </a>
        )}

        <div className="flex gap-3">
          {currentStep > 0 && (
            <Button variant="secondary" onClick={() => setCurrentStep((i) => i - 1)}>
              Back
            </Button>
          )}
          <Button
            onClick={() => {
              toggleStep(currentStep);
              if (currentStep < steps.length - 1) {
                setCurrentStep((i) => i + 1);
              }
            }}
            className="flex-1"
          >
            {currentStep === steps.length - 1 ? "Done!" : "Done, Next"}
          </Button>
        </div>

        <div className="mt-4 flex gap-1">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 flex-1 rounded-full ${
                completed.has(i) ? "bg-safe" : i === currentStep ? "bg-brand" : "bg-card-edge"
              }`}
            />
          ))}
        </div>
      </Card>
    );
  }

  // Analyst mode: all steps at once
  return (
    <Card>
      <h3 className="text-lg font-bold text-text-primary mb-1">
        {checklist.category_label || "Recovery Checklist"}
      </h3>
      <p className="text-sm text-text-muted mb-4">
        {completed.size} of {steps.length} steps completed
      </p>

      <div className="grid gap-2">
        {steps.map((step, i) => (
          <label
            key={i}
            className={`flex items-start gap-3 rounded-xl border p-3 cursor-pointer transition-colors ${
              completed.has(i)
                ? "border-safe/30 bg-emerald-50"
                : "border-card-edge hover:bg-bg-base"
            }`}
          >
            <input
              type="checkbox"
              checked={completed.has(i)}
              onChange={() => toggleStep(i)}
              className="mt-0.5 h-5 w-5 rounded accent-safe"
            />
            <div className="flex-1">
              <p className={`font-medium ${completed.has(i) ? "line-through text-text-muted" : "text-text-primary"}`}>
                {step.title}
              </p>
              <p className="text-sm text-text-muted">{step.description}</p>
              {step.action_url && (
                <a
                  href={step.action_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mt-1 text-sm text-brand hover:underline"
                >
                  {step.action_label || "Open Link"}
                </a>
              )}
            </div>
          </label>
        ))}
      </div>

      {checklist.emergency_contacts && checklist.emergency_contacts.length > 0 && (
        <div className="mt-6 rounded-xl border border-danger/30 bg-red-50 p-4">
          <p className="font-semibold text-danger mb-2">Emergency Contacts</p>
          {checklist.emergency_contacts.map((contact, i) => (
            <p key={i} className="text-sm text-text-primary">
              {contact.name}: <span className="font-medium">{contact.value}</span>
            </p>
          ))}
        </div>
      )}
    </Card>
  );
}
