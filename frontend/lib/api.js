const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8880";

class ApiError extends Error {
  constructor(status, detail) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function request(path, options = {}) {
  const url = `${BASE_URL.replace(/\/$/, "")}${path}`;
  const res = await fetch(url, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {}
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const auth = {
  register: (email, password) =>
    request("/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  login: (email, password) =>
    request("/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: () =>
    request("/v1/auth/logout", { method: "POST" }),
  me: () =>
    request("/v1/auth/me"),
  updateProfile: (data) =>
    request("/v1/auth/profile", {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  rotateApiKey: () =>
    request("/v1/auth/rotate-api-key", { method: "POST" }),
};

export const scans = {
  analyze: (scanType, content) =>
    request("/v1/scan", {
      method: "POST",
      body: JSON.stringify({ scan_type: scanType, content }),
    }),
  history: (limit = 50, offset = 0) =>
    request(`/v1/scan/history?limit=${limit}&offset=${offset}`),
};

export const recovery = {
  getQuestions: () =>
    request("/v1/recovery/triage/questions"),
  submitTriage: (answers) =>
    request("/v1/recovery/triage", {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),
  getChecklist: (category) =>
    request(`/v1/recovery/checklist/${category}`),
};

export { ApiError };
