"use client";

import { useEffect, useState } from "react";
import { useUXMode } from "lib/ux-mode-context";
import { recovery } from "lib/api";
import Card from "components/ui/Card";
import Button from "components/ui/Button";
import Spinner from "components/ui/Spinner";

export default function TriageWizard({ onComplete }) {
  const { isGrandmaMode } = useUXMode();
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    recovery
      .getQuestions()
      .then((data) => setQuestions(data.questions || []))
      .catch(() => setError("Failed to load triage questions."))
      .finally(() => setLoading(false));
  }, []);

  function selectOption(questionId, optionId) {
    setAnswers((prev) => ({ ...prev, [questionId]: optionId }));
    if (isGrandmaMode && currentIndex < questions.length - 1) {
      setCurrentIndex((i) => i + 1);
    }
  }

  async function handleSubmit() {
    setSubmitting(true);
    setError("");
    try {
      const answerList = Object.entries(answers).map(([qId, oId]) => ({
        question_id: qId,
        selected_option_id: oId,
      }));
      const checklist = await recovery.submitTriage(answerList);
      onComplete(checklist);
    } catch (err) {
      setError(err.detail || "Failed to submit triage.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error && !questions.length) {
    return (
      <Card>
        <p className="text-danger font-medium">{error}</p>
      </Card>
    );
  }

  const answeredCount = Object.keys(answers).length;

  // Grandma mode: one question at a time
  if (isGrandmaMode) {
    const q = questions[currentIndex];
    if (!q) return null;

    return (
      <Card>
        <p className="text-sm text-text-muted mb-2">
          Question {currentIndex + 1} of {questions.length}
        </p>
        <h3 className="text-xl font-semibold text-text-primary mb-4">{q.text}</h3>
        <div className="grid gap-3">
          {q.options?.map((opt) => (
            <Button
              key={opt.id}
              variant={answers[q.id] === opt.id ? "primary" : "secondary"}
              size="lg"
              onClick={() => selectOption(q.id, opt.id)}
              className="w-full text-left justify-start text-lg"
            >
              {opt.text}
            </Button>
          ))}
        </div>

        {error && <p className="text-danger text-sm mt-3">{error}</p>}

        <div className="mt-6 flex gap-3">
          {currentIndex > 0 && (
            <Button
              variant="secondary"
              onClick={() => setCurrentIndex((i) => i - 1)}
            >
              Back
            </Button>
          )}
          {currentIndex === questions.length - 1 && answeredCount > 0 && (
            <Button onClick={handleSubmit} loading={submitting} className="flex-1">
              Get My Recovery Plan
            </Button>
          )}
        </div>
      </Card>
    );
  }

  // Analyst mode: all questions at once
  return (
    <Card>
      <h3 className="text-lg font-bold text-text-primary mb-4">Triage Questions</h3>
      <div className="grid gap-6">
        {questions.map((q) => (
          <div key={q.id}>
            <p className="font-medium text-text-primary mb-2">{q.text}</p>
            <div className="flex flex-wrap gap-2">
              {q.options?.map((opt) => (
                <Button
                  key={opt.id}
                  variant={answers[q.id] === opt.id ? "primary" : "secondary"}
                  size="sm"
                  onClick={() => selectOption(q.id, opt.id)}
                >
                  {opt.text}
                </Button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {error && <p className="text-danger text-sm mt-3">{error}</p>}

      <Button
        onClick={handleSubmit}
        loading={submitting}
        disabled={answeredCount === 0}
        className="mt-6"
      >
        Submit Triage
      </Button>
    </Card>
  );
}
