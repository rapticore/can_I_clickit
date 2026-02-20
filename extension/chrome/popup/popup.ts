import type {
  PageTrustScore,
  ThreatLevel,
  ScanResult,
  ScanCountResponse,
} from "../shared/types.js";

const VERDICT_COLORS: Record<ThreatLevel, string> = {
  safe: "#12B76A",
  low: "#12B76A",
  medium: "#F79009",
  high: "#F04438",
  critical: "#D92D20",
};

const VERDICT_LABELS: Record<ThreatLevel, string> = {
  safe: "Safe",
  low: "Low Risk",
  medium: "Suspicious",
  high: "Dangerous",
  critical: "Critical Threat",
};

function $(id: string): HTMLElement {
  return document.getElementById(id)!;
}

async function loadPageTrust(): Promise<void> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.url) return;

  try {
    const domain = new URL(tab.url).hostname;
    $("domain-label").textContent = domain;
  } catch {
    $("domain-label").textContent = "—";
  }

  const stored = await chrome.storage.local.get("current_page_trust");
  const trust = stored.current_page_trust as PageTrustScore | undefined;

  if (trust) {
    renderTrust(trust);
  } else {
    chrome.runtime.sendMessage(
      { type: "GET_PAGE_TRUST", payload: tab.url },
      (response: { trust?: PageTrustScore }) => {
        if (response?.trust) {
          renderTrust(response.trust);
        }
      }
    );
  }
}

function renderTrust(trust: PageTrustScore): void {
  const score = Math.round(trust.score);
  const color = VERDICT_COLORS[trust.verdict];

  $("score-value").textContent = String(score);
  $("verdict-label").textContent = VERDICT_LABELS[trust.verdict];
  $("verdict-label").style.color = color;
  $("domain-label").textContent = trust.domain;

  const circle = $("score-circle") as unknown as SVGCircleElement;
  const circumference = 2 * Math.PI * 42;
  circle.style.strokeDasharray = `${circumference}`;
  circle.style.strokeDashoffset = `${circumference * (1 - score / 100)}`;
  circle.style.stroke = color;

  if (trust.domain_age_days !== null) {
    const years = Math.floor(trust.domain_age_days / 365);
    const months = Math.floor((trust.domain_age_days % 365) / 30);
    $("domain-age").textContent =
      years > 0 ? `${years}y ${months}m` : `${trust.domain_age_days}d`;
  } else {
    $("domain-age").textContent = "Unknown";
  }

  $("ssl-status").textContent = trust.ssl_valid ? "✓ Valid" : "✕ Invalid";
  $("ssl-status").style.color = trust.ssl_valid ? "#12B76A" : "#D92D20";

  $("last-scan").textContent = formatTime(trust.last_scanned);

  if (trust.summary) {
    $("summary-text").textContent = trust.summary;
    $("summary-section").style.display = "block";
  }
}

async function loadLastScan(): Promise<void> {
  const stored = await chrome.storage.local.get("last_scan_result");
  const result = stored.last_scan_result as ScanResult | undefined;

  if (result?.summary) {
    $("summary-text").textContent = result.summary;
    $("summary-section").style.display = "block";
    $("last-scan").textContent = formatTime(result.scanned_at);
  }
}

async function loadScanCount(): Promise<void> {
  chrome.runtime.sendMessage(
    { type: "GET_SCAN_COUNT" },
    (response: ScanCountResponse) => {
      if (!response) return;
      const remaining = response.remaining;
      const pct = (response.scans_today / response.daily_limit) * 100;

      $("usage-fill").style.width = `${Math.min(100, pct)}%`;
      $("usage-fill").style.background = pct >= 100 ? "#D92D20" : "#2E90FA";
      $("usage-label").textContent = `${remaining} scan${remaining !== 1 ? "s" : ""} remaining today (free tier)`;
    }
  );
}

function formatTime(isoString: string): string {
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60_000);

    if (diffMin < 1) return "Just now";
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `${diffHr}h ago`;
    return date.toLocaleDateString();
  } catch {
    return "—";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadPageTrust();
  loadLastScan();
  loadScanCount();
});
