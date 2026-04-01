"use client";

import { useState } from "react";
import { useAuth } from "lib/auth-context";
import { auth as authApi } from "lib/api";
import Card from "components/ui/Card";
import Button from "components/ui/Button";
import Modal from "components/ui/Modal";

export default function ApiKeyPanel() {
  const { user, refreshUser } = useAuth();
  const [showKey, setShowKey] = useState(false);
  const [copied, setCopied] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [rotating, setRotating] = useState(false);

  const apiKey = user?.api_key || "";
  const masked = apiKey ? apiKey.slice(0, 8) + "\u2022".repeat(24) + apiKey.slice(-8) : "No API key";

  function copyKey() {
    if (!apiKey) return;
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function handleRotate() {
    setRotating(true);
    try {
      await authApi.rotateApiKey();
      await refreshUser();
      setConfirmOpen(false);
      setShowKey(true);
    } catch {
      // Silently fail
    } finally {
      setRotating(false);
    }
  }

  return (
    <>
      <Card>
        <h2 className="text-lg font-bold text-text-primary mb-4">API Key</h2>

        <div className="rounded-xl border border-card-edge bg-bg-base p-3 mb-4">
          <code className="block break-all font-mono text-sm text-text-primary">
            {showKey ? apiKey : masked}
          </code>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowKey(!showKey)}
          >
            {showKey ? "Hide" : "Show"}
          </Button>
          <Button variant="secondary" size="sm" onClick={copyKey}>
            {copied ? "Copied!" : "Copy"}
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={() => setConfirmOpen(true)}
          >
            Regenerate
          </Button>
        </div>
      </Card>

      <Modal
        open={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        title="Regenerate API Key?"
      >
        <p className="text-sm text-text-muted mb-4">
          This will invalidate your current API key. Any integrations using it
          will stop working.
        </p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => setConfirmOpen(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleRotate} loading={rotating}>
            Regenerate
          </Button>
        </div>
      </Modal>
    </>
  );
}
