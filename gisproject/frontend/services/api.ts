import axios from "axios";
import type { AxiosProgressEvent, AxiosRequestConfig, AxiosResponse, ResponseType } from "axios";

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";

interface RequestOptions {
  headers?: Record<string, string>;
  params?: Record<string, string | number>;
  body?: any;
  responseType?: "json" | "blob" | "text";
  onDownloadProgress?: (progressEvent: AxiosProgressEvent) => void;
  onUploadProgress?: (progressEvent: AxiosProgressEvent) => void;
  signal?: AbortSignal;
}

const BACKEND_BASE_URLS: Array<{ prefix: string; baseUrl?: string }> = [
  { prefix: "/api", baseUrl: process.env.NEXT_PUBLIC_API_URL },  
  { prefix: "/fastapi", baseUrl: process.env.NEXT_PUBLIC_FASTAPI_API_URL },
  
];


function resolveUrl(endpoint: string): string {
  if (/^https?:\/\//i.test(endpoint)) return endpoint;
  const match = BACKEND_BASE_URLS.find(({ prefix }) => endpoint.startsWith(prefix));
  return match?.baseUrl ? `${match.baseUrl}${endpoint}` : endpoint;
}

function extractMessage(data: any): string {
  if (!data) return "Something went wrong";
  if (typeof data === "string") return data;

  const detail = data?.detail;

  if (!detail) return data?.message ?? data?.error ?? "Something went wrong";

  if (Array.isArray(detail)) {
    return detail
      .map((err: any) => {
        const loc = Array.isArray(err.loc)
          ? err.loc.filter((l: any) => l !== "body").join(" → ")
          : "";
        const msg = err.msg ?? "Invalid value";
        return loc ? `${loc}: ${msg}` : msg;
      })
      .join("; ");
  }

  if (typeof detail === "string") return detail;

  return data?.message ?? data?.error ?? "Something went wrong";
}

export class ApiError extends Error {
  readonly status: number;
  readonly data: any;

  constructor(status: number, data: any) {
    super(extractMessage(data));
    this.status = status;
    this.data = data;
    this.name = "ApiError";
  }
}

const axiosInstance = axios.create({
  withCredentials: true,
});

async function callBackend(
  method: HttpMethod,
  endpoint: string,
  options: RequestOptions = {},
): Promise<AxiosResponse> {
  const { headers = {}, params, body, responseType, onDownloadProgress, onUploadProgress, signal } = options;

  const isFormData = body instanceof FormData;

  const axiosResponseType: ResponseType =
    responseType === "blob" ? "blob" :
    responseType === "text" ? "text" : "json";

  const config: AxiosRequestConfig = {
    method,
    url: resolveUrl(endpoint),
    params,
    withCredentials: true,
    responseType: axiosResponseType,
    onDownloadProgress,
    onUploadProgress,
    signal,
    headers: {
      ...(isFormData ? {} : body ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
    ...(body ? { data: isFormData ? body : body } : {}), 
  };

  return axiosInstance.request(config);
}

export async function request<T>(
  method: HttpMethod,
  endpoint: string,
  options: RequestOptions = {},
): Promise<{ status: number; message: T | null }> {
  try {
    const res = await callBackend(method, endpoint, options);
    const data = res.status === 204 ? null : (res.data as T);
    return { status: res.status, message: data };
  } catch (error: any) {
    if (axios.isAxiosError(error) && error.response) {
      throw new ApiError(error.response.status, error.response.data);
    }
    throw error;
  }
}

export const api = {
  get: <T>(url: string, options?: RequestOptions) =>
    request<T>("GET", url, options),

  post: <T>(url: string, options?: RequestOptions) =>
    request<T>("POST", url, options),

  put: <T>(url: string, options?: RequestOptions) =>
    request<T>("PUT", url, options),

  delete: <T>(url: string, options?: RequestOptions) =>
    request<T>("DELETE", url, options),
};