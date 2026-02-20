import { showTooltip, updateTooltip, removeTooltip } from "./tooltip.js";
import { showInterstitial } from "./interstitial.js";
import type {
  ScanResult,
  TooltipData,
  InterstitialData,
  ScanUrlMessage,
  BadgeFallbackMessage,
} from "../shared/types.js";

const HOVER_DEBOUNCE_MS = 300;

let hoverTimer: ReturnType<typeof setTimeout> | null = null;
let currentHoverUrl: string | null = null;
let pendingResults = new Map<string, ScanResult>();
let cspBlocked = false;

function init(): void {
  detectCSPRestrictions();
  document.addEventListener("mouseover", onMouseOver, { passive: true });
  document.addEventListener("mouseout", onMouseOut, { passive: true });
  document.addEventListener("click", onLinkClick, true);
}

function detectCSPRestrictions(): void {
  try {
    const testEl = document.createElement("div");
    testEl.attachShadow({ mode: "closed" });
    document.body.appendChild(testEl);
    testEl.remove();
    cspBlocked = false;
  } catch {
    cspBlocked = true;
  }
}

function getAnchorFromEvent(e: Event): HTMLAnchorElement | null {
  let el = e.target as HTMLElement | null;
  while (el) {
    if (el.tagName === "A" && (el as HTMLAnchorElement).href) {
      return el as HTMLAnchorElement;
    }
    el = el.parentElement;
  }
  return null;
}

function isExternalUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

function onMouseOver(e: Event): void {
  const anchor = getAnchorFromEvent(e);
  if (!anchor || !isExternalUrl(anchor.href)) return;

  const url = anchor.href;
  if (url === currentHoverUrl) return;

  clearHoverTimer();
  currentHoverUrl = url;

  hoverTimer = setTimeout(() => {
    handleHover(url, e as MouseEvent);
  }, HOVER_DEBOUNCE_MS);
}

function onMouseOut(e: Event): void {
  const anchor = getAnchorFromEvent(e);
  if (!anchor) return;

  clearHoverTimer();
  currentHoverUrl = null;
  removeTooltip();
}

function clearHoverTimer(): void {
  if (hoverTimer !== null) {
    clearTimeout(hoverTimer);
    hoverTimer = null;
  }
}

function handleHover(url: string, e: MouseEvent): void {
  const cached = pendingResults.get(url);
  if (cached) {
    showResult(e.clientX, e.clientY, url, cached);
    return;
  }

  const loadingData: TooltipData = {
    url,
    verdict: "medium",
    confidence: "low",
    summary: "",
    domain_age_days: null,
    loading: true,
  };

  if (!cspBlocked) {
    showTooltip(e.clientX, e.clientY, loadingData);
  }

  const message: ScanUrlMessage = {
    type: "SCAN_URL",
    payload: {
      url,
      source_page: window.location.href,
      hover_context: true,
    },
  };

  chrome.runtime.sendMessage(message, (response: { result?: ScanResult; error?: string }) => {
    if (chrome.runtime.lastError || !response?.result) {
      removeTooltip();
      return;
    }

    const result = response.result;
    pendingResults.set(url, result);

    if (currentHoverUrl === url) {
      if (cspBlocked) {
        sendBadgeFallback(result);
      } else {
        showResult(e.clientX, e.clientY, url, result);
      }
    }
  });
}

function showResult(x: number, y: number, url: string, result: ScanResult): void {
  const tooltipData: TooltipData = {
    url,
    verdict: result.verdict,
    confidence: result.confidence,
    summary: result.summary,
    domain_age_days: result.domain_info?.age_days ?? null,
  };

  try {
    if (document.getElementById("cici-tooltip-host")) {
      updateTooltip(tooltipData);
    } else {
      showTooltip(x, y, tooltipData);
    }
  } catch {
    sendBadgeFallback(result);
  }
}

function sendBadgeFallback(result: ScanResult): void {
  const message: BadgeFallbackMessage = {
    type: "BADGE_FALLBACK",
    payload: {
      verdict: result.verdict,
      summary: result.summary,
    },
  };
  chrome.runtime.sendMessage(message);
}

function onLinkClick(e: MouseEvent): void {
  const anchor = getAnchorFromEvent(e);
  if (!anchor || !isExternalUrl(anchor.href)) return;

  const url = anchor.href;
  const result = pendingResults.get(url);

  if (!result) return;

  if (result.verdict === "critical" || result.verdict === "high") {
    e.preventDefault();
    e.stopPropagation();

    const interstitialData: InterstitialData = {
      url,
      verdict: result.verdict,
      consequence_warning: result.consequence_warning ?? "This link has been flagged as dangerous. Proceeding could expose your personal information or device to threats.",
      safe_action_suggestion: result.safe_action_suggestion ?? "Navigate to the website directly by typing the address in your browser instead of clicking this link.",
      threat_summary: result.summary,
    };

    if (cspBlocked) {
      const proceed = confirm(
        `⚠️ Can I Click It? — Warning\n\n` +
        `${interstitialData.threat_summary}\n\n` +
        `${interstitialData.consequence_warning}\n\n` +
        `Click OK to proceed anyway, or Cancel to go back to safety.`
      );
      if (proceed) {
        navigateToUrl(url);
      }
    } else {
      showInterstitial(
        interstitialData,
        () => { /* go back — do nothing */ },
        () => navigateToUrl(url)
      );
    }
  }
}

function navigateToUrl(url: string): void {
  window.location.href = url;
}

init();
