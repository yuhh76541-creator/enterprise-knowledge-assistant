import type { Health, KnowledgeBase } from "../types";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(`/api/v1${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers },
      signal: controller.signal,
    });
    if (!response.ok) {
      const body: unknown = await response.json().catch(() => null);
      const detail =
        body && typeof body === "object" && "detail" in body
          ? body.detail
          : null;
      throw new Error(
        typeof detail === "string" ? detail : "请求未完成，请检查输入后重试。",
      );
    }
    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("连接超时，请确认本机服务已启动。");
    }
    if (error instanceof TypeError)
      throw new Error("无法连接本机服务，请检查启动状态。");
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export const api = {
  health: () => request<Health>("/health"),
  spaces: () => request<KnowledgeBase[]>("/knowledge-bases"),
  createSpace: (name: string, description: string) =>
    request<KnowledgeBase>("/knowledge-bases", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    }),
};
