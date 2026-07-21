import type { DocumentItem, IndexMode, IndexStatus, QueryResponse, User } from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? "Request failed");
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export const api = {
  loginUrl: `${API_URL}/auth/login`,
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  me: () => request<User>("/me"),
  startIndex: (mode: IndexMode) => request<{ message: string }>("/drive/index", { method: "POST", body: JSON.stringify({ mode }) }),
  indexStatus: () => request<IndexStatus>("/drive/index/status"),
  documents: () => request<DocumentItem[]>("/documents"),
  query: (question: string, documentId?: number) => request<QueryResponse>("/query", { method: "POST", body: JSON.stringify({ question, document_id: documentId }) }),
  deleteData: () => request<{ message: string }>("/user/data", { method: "DELETE" }),
  feedback: (message: string, email?: string) =>
    request<{ message: string }>("/feedback", { method: "POST", body: JSON.stringify({ message, email }) })
};
