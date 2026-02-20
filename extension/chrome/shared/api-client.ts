import type { ScanRequest, ScanResult, PageTrustScore } from "./types.js";

const DEFAULT_BASE_URL = "http://localhost:8880";

interface ApiClientConfig {
  baseUrl: string;
  apiKey: string;
}

interface ApiErrorResponse {
  detail?: string;
  message?: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function getConfig(): Promise<ApiClientConfig> {
  const result = await chrome.storage.sync.get({
    api_base_url: DEFAULT_BASE_URL,
    api_key: "",
  });
  return {
    baseUrl: result.api_base_url,
    apiKey: result.api_key,
  };
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const config = await getConfig();
  const url = `${config.baseUrl}${path}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Client-Schema": "legacy",
    ...(config.apiKey ? { "X-API-Key": config.apiKey } : {}),
    ...(options.headers as Record<string, string> ?? {}),
  };

  let response: Response;
  try {
    response = await fetch(url, { ...options, headers });
  } catch {
    throw new ApiError(
      "Unable to reach the Can I Click It? service. Check your connection and try again.",
      0
    );
  }

  if (!response.ok) {
    let detail: string | undefined;
    try {
      const body: ApiErrorResponse = await response.json();
      detail = body.detail ?? body.message;
    } catch {
      // response body wasn't JSON
    }
    throw new ApiError(
      detail ?? `Request failed (${response.status})`,
      response.status,
      detail
    );
  }

  return response.json() as Promise<T>;
}

export async function scanUrl(
  content: string,
  sourcePage?: string
): Promise<ScanResult> {
  const body: ScanRequest = {
    scan_type: "url",
    content,
    metadata: sourcePage ? { source_page: sourcePage, hover_context: true } : undefined,
  };
  return request<ScanResult>("/v1/scan", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function getPageTrust(url: string): Promise<PageTrustScore> {
  return request<PageTrustScore>(
    `/v1/page-trust?url=${encodeURIComponent(url)}`
  );
}

export function fallbackScanResult(url: string, errorMsg: string): ScanResult {
  return {
    scan_id: "fallback",
    verdict: "medium",
    confidence: "low",
    summary: errorMsg,
    signals: [],
    scan_type: "url",
    scanned_at: new Date().toISOString(),
  };
}
