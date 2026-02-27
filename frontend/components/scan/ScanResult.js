"use client";

import { useUXMode } from "lib/ux-mode-context";
import GrandmaResult from "./GrandmaResult";
import AnalystResult from "./AnalystResult";

export default function ScanResult({ result }) {
  const { isGrandmaMode } = useUXMode();

  if (isGrandmaMode) {
    return <GrandmaResult result={result} />;
  }

  return <AnalystResult result={result} />;
}
