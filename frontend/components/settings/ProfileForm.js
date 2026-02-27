"use client";

import { useState } from "react";
import { useAuth } from "lib/auth-context";
import { auth as authApi } from "lib/api";
import Card from "components/ui/Card";
import Button from "components/ui/Button";

const languages = [
  { code: "en", label: "English" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "de", label: "German" },
  { code: "pt", label: "Portuguese" },
  { code: "zh", label: "Chinese" },
  { code: "ja", label: "Japanese" },
  { code: "ko", label: "Korean" },
];

export default function ProfileForm() {
  const { user, refreshUser } = useAuth();
  const [language, setLanguage] = useState(user?.language || "en");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    try {
      await authApi.updateProfile({ language });
      await refreshUser();
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // Silently fail
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card>
      <h2 className="text-lg font-bold text-text-primary mb-4">Profile</h2>

      <div className="grid gap-4">
        <div className="grid gap-1.5">
          <label className="text-sm font-medium text-text-muted">Email</label>
          <input
            type="email"
            value={user?.email || ""}
            disabled
            className="w-full rounded-xl border border-card-edge bg-bg-base px-3 py-2.5 text-text-muted"
          />
        </div>

        <div className="grid gap-1.5">
          <label htmlFor="language" className="text-sm font-medium text-text-muted">
            Language
          </label>
          <select
            id="language"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full rounded-xl border border-card-edge bg-white px-3 py-2.5 text-text-primary focus:outline-none focus:ring-2 focus:ring-brand/40"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.label}
              </option>
            ))}
          </select>
        </div>

        <Button onClick={handleSave} loading={saving} size="sm">
          {saved ? "Saved!" : "Save Changes"}
        </Button>
      </div>
    </Card>
  );
}
