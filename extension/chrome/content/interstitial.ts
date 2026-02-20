import type { InterstitialData } from "../shared/types.js";

const INTERSTITIAL_ID = "cici-interstitial-host";
const RECOVERY_URL = "https://app.caniclickit.com/recovery";

function getInterstitialCSS(): string {
  return `
    :host {
      all: initial;
      position: fixed;
      inset: 0;
      z-index: 999999;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .cici-interstitial {
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(16, 24, 40, 0.7);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
    }

    .cici-interstitial__card {
      background: #FFFFFF;
      border-radius: 12px;
      box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
      max-width: 480px;
      width: calc(100% - 32px);
      padding: 32px;
      text-align: center;
    }

    .cici-interstitial__icon {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: #FEE4E2;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 20px;
      font-size: 28px;
    }

    .cici-interstitial__title {
      font-size: 20px;
      font-weight: 700;
      color: #101828;
      margin-bottom: 8px;
    }

    .cici-interstitial__threat {
      display: inline-block;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 4px 10px;
      border-radius: 16px;
      background: #FEF3F2;
      color: #D92D20;
      margin-bottom: 16px;
    }

    .cici-interstitial__summary {
      font-size: 15px;
      color: #344054;
      line-height: 1.5;
      margin-bottom: 12px;
    }

    .cici-interstitial__consequence {
      font-size: 13px;
      color: #D92D20;
      background: #FEF3F2;
      border: 1px solid #FECDCA;
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 12px;
      line-height: 1.4;
      text-align: left;
    }

    .cici-interstitial__safe-action {
      font-size: 13px;
      color: #027A48;
      background: #ECFDF3;
      border: 1px solid #ABEFC6;
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 24px;
      line-height: 1.4;
      text-align: left;
    }

    .cici-interstitial__safe-action strong,
    .cici-interstitial__consequence strong {
      display: block;
      margin-bottom: 4px;
    }

    .cici-interstitial__actions {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 16px;
    }

    .cici-interstitial__btn-primary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 12px 24px;
      background: #2E90FA;
      color: #FFFFFF;
      font-size: 15px;
      font-weight: 600;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.15s;
    }

    .cici-interstitial__btn-primary:hover {
      background: #1570EF;
    }

    .cici-interstitial__btn-secondary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 10px 20px;
      background: transparent;
      color: #667085;
      font-size: 13px;
      font-weight: 500;
      border: 1px solid #D0D5DD;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.15s, color 0.15s;
    }

    .cici-interstitial__btn-secondary:hover {
      background: #F8FAFC;
      color: #344054;
    }

    .cici-interstitial__recovery-link {
      display: block;
      font-size: 13px;
      color: #2E90FA;
      text-decoration: none;
      margin-bottom: 16px;
      cursor: pointer;
    }

    .cici-interstitial__recovery-link:hover {
      text-decoration: underline;
    }

    .cici-interstitial__disclaimer {
      font-size: 11px;
      color: #98A2B3;
      line-height: 1.4;
    }
  `;
}

function buildInterstitialHTML(data: InterstitialData): string {
  const threatLabel = data.verdict === "critical" ? "Critical Threat" : "Dangerous";

  return `
    <div class="cici-interstitial">
      <div class="cici-interstitial__card">
        <div class="cici-interstitial__icon">⚠️</div>
        <div class="cici-interstitial__title">This link may be dangerous</div>
        <div class="cici-interstitial__threat">${threatLabel}</div>
        <div class="cici-interstitial__summary">${escapeHtml(data.threat_summary)}</div>
        <div class="cici-interstitial__consequence">
          <strong>What could happen:</strong>
          ${escapeHtml(data.consequence_warning)}
        </div>
        <div class="cici-interstitial__safe-action">
          <strong>What to do instead:</strong>
          ${escapeHtml(data.safe_action_suggestion)}
        </div>
        <div class="cici-interstitial__actions">
          <button class="cici-interstitial__btn-primary" data-action="go-back">Go Back to Safety</button>
          <button class="cici-interstitial__btn-secondary" data-action="proceed">Proceed Anyway</button>
        </div>
        <a class="cici-interstitial__recovery-link" data-action="recovery">What do I do now?</a>
        <div class="cici-interstitial__disclaimer">
          This analysis is our best assessment based on available signals. Always verify
          directly with the sender if you are unsure. This guidance is informational and
          not a substitute for professional security or legal advice.
        </div>
      </div>
    </div>
  `;
}

function escapeHtml(str: string): string {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

export function showInterstitial(
  data: InterstitialData,
  onGoBack: () => void,
  onProceed: () => void
): void {
  removeInterstitial();

  const host = document.createElement("div");
  host.id = INTERSTITIAL_ID;
  const shadow = host.attachShadow({ mode: "closed" });

  const style = document.createElement("style");
  style.textContent = getInterstitialCSS();
  shadow.appendChild(style);

  const container = document.createElement("div");
  container.innerHTML = buildInterstitialHTML(data);
  shadow.appendChild(container);

  container.addEventListener("click", (e) => {
    const target = e.target as HTMLElement;
    const action = target.dataset.action;

    if (action === "go-back") {
      removeInterstitial();
      onGoBack();
    } else if (action === "proceed") {
      removeInterstitial();
      onProceed();
    } else if (action === "recovery") {
      window.open(RECOVERY_URL, "_blank", "noopener");
    }
  });

  // Close on Escape key
  const escHandler = (e: KeyboardEvent) => {
    if (e.key === "Escape") {
      removeInterstitial();
      onGoBack();
      document.removeEventListener("keydown", escHandler);
    }
  };
  document.addEventListener("keydown", escHandler);

  document.body.appendChild(host);
}

export function removeInterstitial(): void {
  document.getElementById(INTERSTITIAL_ID)?.remove();
}

export function isInterstitialVisible(): boolean {
  return !!document.getElementById(INTERSTITIAL_ID);
}
