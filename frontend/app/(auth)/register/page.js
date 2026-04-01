"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Card from "components/ui/Card";
import Input from "components/ui/Input";
import Button from "components/ui/Button";
import { useAuth } from "lib/auth-context";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [copied, setCopied] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      const data = await register(email, password);
      setApiKey(data.api_key);
    } catch (err) {
      setError(err.detail || err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  function copyKey() {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (apiKey) {
    return (
      <Card>
        <h1 className="text-2xl font-bold text-text-primary mb-1">
          Account created
        </h1>
        <p className="text-text-muted mb-4">
          Your API key has been generated. Save it now — you won&apos;t see it again.
        </p>

        <div className="rounded-xl border border-warning/30 bg-amber-50 p-4 mb-4">
          <p className="text-sm font-semibold text-warning mb-2">
            Your API Key
          </p>
          <code className="block break-all rounded-lg bg-white border border-card-edge p-3 text-sm font-mono text-text-primary">
            {apiKey}
          </code>
          <Button
            variant="secondary"
            size="sm"
            onClick={copyKey}
            className="mt-3"
          >
            {copied ? "Copied!" : "Copy to clipboard"}
          </Button>
        </div>

        <Button onClick={() => router.push("/dashboard")} className="w-full">
          Go to Dashboard
        </Button>
      </Card>
    );
  }

  return (
    <Card>
      <h1 className="text-2xl font-bold text-text-primary mb-1">
        Create your account
      </h1>
      <p className="text-text-muted mb-6">
        Get started with Can I Click It?
      </p>

      <form onSubmit={handleSubmit} className="grid gap-4">
        <Input
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />
        <Input
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="new-password"
          minLength={8}
        />
        <Input
          label="Confirm Password"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          autoComplete="new-password"
        />

        {error && (
          <p className="text-sm text-danger font-medium" role="alert">
            {error}
          </p>
        )}

        <Button type="submit" loading={loading} className="w-full">
          Create account
        </Button>
      </form>

      <p className="mt-4 text-center text-sm text-text-muted">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-brand">
          Sign in
        </Link>
      </p>
    </Card>
  );
}
