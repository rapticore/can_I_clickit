export type ThreatLevel = "critical" | "high" | "medium" | "low" | "safe";

export type ConfidenceLevel = "high" | "medium" | "low";

export type ScanType = "url" | "text" | "screenshot" | "qr" | "qr_code";

export interface ScanRequest {
  scan_type: ScanType;
  content: string;
  metadata?: {
    source_page?: string;
    hover_context?: boolean;
  };
}

export interface SignalResult {
  signal_name: string;
  value: string | number | boolean;
  risk_contribution: ThreatLevel;
  detail?: string;
}

export interface ScanResult {
  scan_id: string;
  verdict: ThreatLevel;
  confidence: ConfidenceLevel;
  summary: string;
  consequence_warning?: string;
  safe_action_suggestion?: string;
  signals: SignalResult[];
  domain_info?: {
    domain: string;
    age_days: number | null;
    ssl_valid: boolean;
    registrar?: string;
  };
  scan_type: ScanType;
  scanned_at: string;
}

export interface PageTrustScore {
  score: number;
  verdict: ThreatLevel;
  confidence: ConfidenceLevel;
  domain: string;
  domain_age_days: number | null;
  ssl_valid: boolean;
  last_scanned: string;
  summary: string;
  signals: SignalResult[];
}

export interface TooltipData {
  url: string;
  verdict: ThreatLevel;
  confidence: ConfidenceLevel;
  summary: string;
  domain_age_days: number | null;
  loading?: boolean;
}

export interface InterstitialData {
  url: string;
  verdict: ThreatLevel;
  consequence_warning: string;
  safe_action_suggestion: string;
  threat_summary: string;
}

export interface ExtensionSettings {
  api_base_url: string;
  api_key: string;
  daily_scan_limit: number;
  scans_today: number;
  last_scan_date: string;
}

export interface BadgeState {
  text: string;
  color: string;
}

export type MessageType =
  | "SCAN_URL"
  | "SCAN_RESULT"
  | "PAGE_TRUST_UPDATE"
  | "SHOW_INTERSTITIAL"
  | "UPDATE_BADGE"
  | "GET_PAGE_TRUST"
  | "GET_SCAN_COUNT"
  | "BADGE_FALLBACK";

export interface ExtensionMessage {
  type: MessageType;
  payload?: unknown;
}

export interface ScanUrlMessage extends ExtensionMessage {
  type: "SCAN_URL";
  payload: {
    url: string;
    source_page: string;
    hover_context?: boolean;
  };
}

export interface ScanResultMessage extends ExtensionMessage {
  type: "SCAN_RESULT";
  payload: ScanResult;
}

export interface PageTrustMessage extends ExtensionMessage {
  type: "PAGE_TRUST_UPDATE";
  payload: PageTrustScore;
}

export interface BadgeFallbackMessage extends ExtensionMessage {
  type: "BADGE_FALLBACK";
  payload: {
    verdict: ThreatLevel;
    summary: string;
  };
}

export interface ScanCountResponse {
  scans_today: number;
  daily_limit: number;
  remaining: number;
}
