"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useAuth } from "./auth-context";
import { auth as authApi } from "./api";

const UXModeContext = createContext(null);

export function UXModeProvider({ children }) {
  const { user } = useAuth();
  const [isGrandmaMode, setIsGrandmaModeState] = useState(false);

  useEffect(() => {
    if (user) {
      setIsGrandmaModeState(user.grandma_mode ?? false);
    }
  }, [user]);

  const setIsGrandmaMode = useCallback(
    async (value) => {
      setIsGrandmaModeState(value);
      try {
        await authApi.updateProfile({ grandma_mode: value });
      } catch {
        // Revert on failure
        setIsGrandmaModeState(!value);
      }
    },
    [],
  );

  return (
    <UXModeContext.Provider value={{ isGrandmaMode, setIsGrandmaMode }}>
      {children}
    </UXModeContext.Provider>
  );
}

export function useUXMode() {
  const ctx = useContext(UXModeContext);
  if (!ctx) throw new Error("useUXMode must be used within UXModeProvider");
  return ctx;
}
