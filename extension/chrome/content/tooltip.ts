import type { TooltipData, ThreatLevel } from "../shared/types.js";

const TOOLTIP_ID = "cici-tooltip-host";

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

const CONFIDENCE_LABELS: Record<string, string> = {
  high: "High confidence",
  medium: "Medium confidence",
  low: "Low confidence",
};

// Static HTML skeletons — contain NO dynamic data.
// All user-controlled values are set via textContent after cloning.
const LOADING_TEMPLATE_HTML = `
  <div class="cici-tooltip" style="border-left-color: #D0D5DD;">
    <div class="cici-tooltip__header">
      <span class="cici-tooltip__spinner"></span>
      <span class="cici-tooltip__title">Analyzing\u2026</span>
    </div>
    <div class="cici-tooltip__url"></div>
  </div>
`;

const TOOLTIP_TEMPLATE_HTML = `
  <div class="cici-tooltip">
    <div class="cici-tooltip__header">
      <span class="cici-tooltip__dot"></span>
      <span class="cici-tooltip__title"></span>
      <span class="cici-tooltip__confidence"></span>
    </div>
    <div class="cici-tooltip__summary"></div>
    <div class="cici-tooltip__meta">
      <span class="cici-tooltip__domain-age"></span>
    </div>
    <div class="cici-tooltip__url"></div>
  </div>
`;

function buildTooltipDOM(data: TooltipData): DocumentFragment {
  const template = document.createElement("template");

  if (data.loading) {
    template.innerHTML = LOADING_TEMPLATE_HTML;
    const content = template.content;
    content.querySelector(".cici-tooltip__url")!.textContent = truncateUrl(data.url);
    return content;
  }

  const color = VERDICT_COLORS[data.verdict];
  const label = VERDICT_LABELS[data.verdict];

  template.innerHTML = TOOLTIP_TEMPLATE_HTML;
  const content = template.content;

  // Apply styles via DOM API (safe — rejects invalid CSS values)
  (content.querySelector(".cici-tooltip") as HTMLElement).style.borderLeftColor = color;
  (content.querySelector(".cici-tooltip__dot") as HTMLElement).style.background = color;

  // Populate dynamic values via textContent (XSS-safe)
  content.querySelector(".cici-tooltip__title")!.textContent = label;
  content.querySelector(".cici-tooltip__confidence")!.textContent = CONFIDENCE_LABELS[data.confidence] ?? "";
  content.querySelector(".cici-tooltip__summary")!.textContent = data.summary;

  const domainAge = data.domain_age_days !== null
    ? `${data.domain_age_days} day${data.domain_age_days !== 1 ? "s" : ""} old`
    : "Unknown age";
  content.querySelector(".cici-tooltip__domain-age")!.textContent = domainAge;
  content.querySelector(".cici-tooltip__url")!.textContent = truncateUrl(data.url);

  return content;
}

function getTooltipCSS(): string {
  return `
    :host {
      all: initial;
      position: fixed;
      z-index: 999998;
      pointer-events: none;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .cici-tooltip {
      background: #FFFFFF;
      border: 1px solid #D0D5DD;
      border-left: 4px solid #D0D5DD;
      border-radius: 6px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12), 0 1px 4px rgba(0, 0, 0, 0.08);
      padding: 12px 14px;
      max-width: 320px;
      min-width: 200px;
      font-size: 13px;
      line-height: 1.4;
      color: #344054;
    }

    .cici-tooltip__header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }

    .cici-tooltip__dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .cici-tooltip__title {
      font-weight: 600;
      font-size: 14px;
      color: #101828;
    }

    .cici-tooltip__confidence {
      font-size: 11px;
      color: #667085;
      margin-left: auto;
    }

    .cici-tooltip__summary {
      font-size: 12px;
      color: #344054;
      margin-bottom: 8px;
    }

    .cici-tooltip__meta {
      display: flex;
      gap: 12px;
      font-size: 11px;
      color: #667085;
      margin-bottom: 6px;
    }

    .cici-tooltip__url {
      font-size: 11px;
      color: #98A2B3;
      word-break: break-all;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .cici-tooltip__spinner {
      width: 14px;
      height: 14px;
      border: 2px solid #D0D5DD;
      border-top-color: #2E90FA;
      border-radius: 50%;
      animation: cici-spin 0.8s linear infinite;
    }

    @keyframes cici-spin {
      to { transform: rotate(360deg); }
    }
  `;
}

function truncateUrl(url: string, max = 60): string {
  return url.length > max ? url.slice(0, max) + "\u2026" : url;
}

export function showTooltip(x: number, y: number, data: TooltipData): void {
  removeTooltip();

  const host = document.createElement("div");
  host.id = TOOLTIP_ID;
  const shadow = host.attachShadow({ mode: "open" });

  const style = document.createElement("style");
  style.textContent = getTooltipCSS();
  shadow.appendChild(style);

  const container = document.createElement("div");
  container.appendChild(buildTooltipDOM(data));
  shadow.appendChild(container);

  document.body.appendChild(host);

  const viewportW = window.innerWidth;
  const viewportH = window.innerHeight;
  const offsetX = 16;
  const offsetY = 20;

  let left = x + offsetX;
  let top = y + offsetY;

  requestAnimationFrame(() => {
    const rect = host.getBoundingClientRect();
    if (left + rect.width > viewportW - 8) {
      left = x - rect.width - offsetX;
    }
    if (top + rect.height > viewportH - 8) {
      top = y - rect.height - offsetY;
    }
    left = Math.max(8, left);
    top = Math.max(8, top);

    host.style.left = `${left}px`;
    host.style.top = `${top}px`;
  });
}

export function updateTooltip(data: TooltipData): void {
  const host = document.getElementById(TOOLTIP_ID);
  if (!host || !host.shadowRoot) return;

  const container = host.shadowRoot.querySelector("div:not(style)") as HTMLElement | null;
  if (!container) return;

  // Clear and rebuild with safe DOM construction
  container.replaceChildren();
  container.appendChild(buildTooltipDOM(data));
}

export function removeTooltip(): void {
  document.getElementById(TOOLTIP_ID)?.remove();
}

export function isTooltipVisible(): boolean {
  return !!document.getElementById(TOOLTIP_ID);
}
