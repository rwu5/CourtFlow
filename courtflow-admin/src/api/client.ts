// In H5 dev mode, vite proxy forwards /api/* to the backend — use empty base.
// In production or non-H5 platforms, use the full URL.
const BASE_URL = (() => {
  // @ts-ignore
  if (import.meta.env.DEV && typeof window !== "undefined") return "";
  return import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
})();

export class ApiError extends Error {
  constructor(public statusCode: number, public detail: string) {
    super(detail);
  }
}

function getToken(): string | null {
  try {
    return uni.getStorageSync("access_token") || null;
  } catch {
    return null;
  }
}

async function request<T>(
  method: "GET" | "POST" | "PUT" | "DELETE",
  path: string,
  options?: {
    data?: Record<string, unknown>;
    params?: Record<string, string | number | boolean>;
    auth?: boolean;
  },
): Promise<T> {
  const { data, params, auth = true } = options ?? {};

  let url = `${BASE_URL}${path}`;
  if (params) {
    const qs = new URLSearchParams(
      Object.entries(params).map(([k, v]) => [k, String(v)]),
    ).toString();
    url = `${url}?${qs}`;
  }

  const header: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (auth) {
    const token = getToken();
    if (token) header["Authorization"] = `Bearer ${token}`;
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url,
      method,
      data: data ? JSON.stringify(data) : undefined,
      header,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T);
        } else {
          const detail =
            (res.data as { detail?: string })?.detail ?? "Request failed";
          reject(new ApiError(res.statusCode, detail));
        }
      },
      fail(err) {
        reject(new ApiError(0, err.errMsg ?? "Network error"));
      },
    });
  });
}

export const http = {
  get: <T>(
    path: string,
    params?: Record<string, string | number | boolean>,
    auth = true,
  ) => request<T>("GET", path, { params, auth }),

  post: <T>(
    path: string,
    data?: Record<string, unknown>,
    auth = true,
  ) => request<T>("POST", path, { data, auth }),

  put: <T>(path: string, data?: Record<string, unknown>) =>
    request<T>("PUT", path, { data }),

  del: <T>(path: string) => request<T>("DELETE", path),
};
