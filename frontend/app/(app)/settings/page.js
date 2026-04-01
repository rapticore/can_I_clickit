"use client";

import { useUXMode } from "lib/ux-mode-context";
import ProfileForm from "components/settings/ProfileForm";
import GrandmaModeToggle from "components/settings/GrandmaModeToggle";
import ApiKeyPanel from "components/settings/ApiKeyPanel";

export default function SettingsPage() {
  const { isGrandmaMode } = useUXMode();

  return (
    <div className="grid gap-6">
      <div>
        <h1 className={`font-bold text-text-primary ${isGrandmaMode ? "text-3xl" : "text-2xl"}`}>
          Settings
        </h1>
        <p className={`text-text-muted mt-1 ${isGrandmaMode ? "text-lg" : "text-sm"}`}>
          Manage your account and preferences.
        </p>
      </div>

      <GrandmaModeToggle />
      <ProfileForm />
      <ApiKeyPanel />
    </div>
  );
}
