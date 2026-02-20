import { scanUrl, getPageTrust, fallbackScanResult } from "../shared/api-client.js";
import type {
  ThreatLevel,
  ScanResult,
  PageTrustScore,
  ExtensionMessage,
  ScanUrlMessage,
  ScanCountResponse,
  BadgeFallbackMessage,
} from "../shared/types.js";

const ALARM_PERIODIC_CHECK = "periodic-page-check";
const ALARM_RESET_DAILY = "reset-daily-count";
const SCAN_CACHE_TTL_MS = 5 * 60 * 1000;

const scanCache = new Map<string, { result: ScanResult; timestamp: number }>();

function verdictToBadge(verdict: ThreatLevel): { text: string; color: string } {
  switch (verdict) {
    case "safe":
    case "low":
      return { text: "✓", color: "#12B76A" };
    case "medium":
      return { text: "!", color: "#F79009" };
    case "high":
    case "critical":
      return { text: "✕", color: "#D92D20" };
  }
}

async function updateBadge(tabId: number, verdict: ThreatLevel): Promise<void> {
  const { text, color } = verdictToBadge(verdict);
  await chrome.action.setBadgeText({ text, tabId });
  await chrome.action.setBadgeBackgroundColor({ color, tabId });
}

async function clearBadge(tabId: number): Promise<void> {
  await chrome.action.setBadgeText({ text: "", tabId });
}

async function incrementScanCount(): Promise<ScanCountResponse> {
  const today = new Date().toISOString().slice(0, 10);
  const data = await chrome.storage.local.get({
    scans_today: 0,
    last_scan_date: "",
    daily_scan_limit: 5,
  });

  let count = data.scans_today as number;
  const limit = data.daily_scan_limit as number;

  if (data.last_scan_date !== today) {
    count = 0;
  }

  count++;
  await chrome.storage.local.set({ scans_today: count, last_scan_date: today });

  return { scans_today: count, daily_limit: limit, remaining: Math.max(0, limit - count) };
}

async function getScanCount(): Promise<ScanCountResponse> {
  const today = new Date().toISOString().slice(0, 10);
  const data = await chrome.storage.local.get({
    scans_today: 0,
    last_scan_date: "",
    daily_scan_limit: 5,
  });

  let count = data.scans_today as number;
  const limit = data.daily_scan_limit as number;

  if (data.last_scan_date !== today) {
    count = 0;
  }

  return { scans_today: count, daily_limit: limit, remaining: Math.max(0, limit - count) };
}

function getCachedResult(url: string): ScanResult | null {
  const cached = scanCache.get(url);
  if (!cached) return null;
  if (Date.now() - cached.timestamp > SCAN_CACHE_TTL_MS) {
    scanCache.delete(url);
    return null;
  }
  return cached.result;
}

async function handleScanUrl(
  payload: ScanUrlMessage["payload"],
  tabId: number
): Promise<ScanResult> {
  const cached = getCachedResult(payload.url);
  if (cached) return cached;

  let result: ScanResult;
  try {
    result = await scanUrl(payload.url, payload.source_page);
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Analysis unavailable";
    result = fallbackScanResult(payload.url, msg);
  }

  scanCache.set(payload.url, { result, timestamp: Date.now() });
  await incrementScanCount();
  await updateBadge(tabId, result.verdict);
  await storeLastScan(result);

  return result;
}

async function storeLastScan(result: ScanResult): Promise<void> {
  await chrome.storage.local.set({ last_scan_result: result });
}

async function handlePageTrust(tabId: number, url: string): Promise<PageTrustScore | null> {
  try {
    const trust = await getPageTrust(url);
    await updateBadge(tabId, trust.verdict);
    await chrome.storage.local.set({ current_page_trust: trust });
    return trust;
  } catch {
    return null;
  }
}

chrome.runtime.onMessage.addListener(
  (message: ExtensionMessage, sender, sendResponse) => {
    const tabId = sender.tab?.id;

    switch (message.type) {
      case "SCAN_URL": {
        const payload = (message as ScanUrlMessage).payload;
        if (!tabId) {
          sendResponse({ error: "No tab context" });
          return false;
        }
        handleScanUrl(payload, tabId).then(
          (result) => sendResponse({ result }),
          (err) => sendResponse({ error: (err as Error).message })
        );
        return true; // async response
      }

      case "GET_PAGE_TRUST": {
        const url = message.payload as string;
        if (!tabId) {
          sendResponse({ error: "No tab context" });
          return false;
        }
        handlePageTrust(tabId, url).then(
          (trust) => sendResponse({ trust }),
          (err) => sendResponse({ error: (err as Error).message })
        );
        return true;
      }

      case "GET_SCAN_COUNT": {
        getScanCount().then(
          (counts) => sendResponse(counts),
          () => sendResponse({ scans_today: 0, daily_limit: 5, remaining: 5 })
        );
        return true;
      }

      case "BADGE_FALLBACK": {
        const fallback = (message as BadgeFallbackMessage).payload;
        if (tabId) {
          updateBadge(tabId, fallback.verdict).then(
            () => sendResponse({ ok: true }),
            () => sendResponse({ ok: false })
          );
        }
        return true;
      }

      case "UPDATE_BADGE": {
        const verdict = message.payload as ThreatLevel;
        if (tabId) {
          updateBadge(tabId, verdict).then(
            () => sendResponse({ ok: true }),
            () => sendResponse({ ok: false })
          );
        }
        return true;
      }

      default:
        return false;
    }
  }
);

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    clearBadge(tabId);
    handlePageTrust(tabId, tab.url);
  }
});

chrome.alarms.create(ALARM_PERIODIC_CHECK, { periodInMinutes: 30 });
chrome.alarms.create(ALARM_RESET_DAILY, {
  when: getNextMidnight(),
  periodInMinutes: 24 * 60,
});

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === ALARM_PERIODIC_CHECK) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab?.id && tab.url) {
      handlePageTrust(tab.id, tab.url);
    }
  }

  if (alarm.name === ALARM_RESET_DAILY) {
    await chrome.storage.local.set({ scans_today: 0, last_scan_date: "" });
  }
});

function getNextMidnight(): number {
  const now = new Date();
  const midnight = new Date(now);
  midnight.setHours(24, 0, 0, 0);
  return midnight.getTime();
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.set({
    api_base_url: "http://localhost:8880",
    api_key: "",
  });
  chrome.storage.local.set({
    scans_today: 0,
    last_scan_date: "",
    daily_scan_limit: 5,
  });
});
