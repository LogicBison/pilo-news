import { NextResponse, type NextRequest } from "next/server";

const API_BASE = process.env.API_INTERNAL_URL ?? "http://api:8080";

const FORWARD_HEADERS = [
  "content-type",
  "cookie",
  "x-csrf-token",
  "x-api-key",
  "user-agent",
  "accept",
  "x-forwarded-for",
];

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const suffix = path[0] === "v1" ? path.join("/") : `v1/${path.join("/")}`;
  const target = `${API_BASE.replace(/\/$/, "")}/${suffix}${request.nextUrl.search}`;
  const headers = new Headers();
  for (const name of FORWARD_HEADERS) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  const body =
    request.method === "GET" || request.method === "HEAD" ? undefined : await request.text();
  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body,
      cache: "no-store",
      redirect: "manual",
    });
    const response = new NextResponse(await upstream.arrayBuffer(), {
      status: upstream.status,
      headers: {
        "content-type": upstream.headers.get("content-type") ?? "application/json",
        "cache-control": "no-store",
      },
    });
    const cookies = upstream.headers.getSetCookie?.() ?? [];
    for (const cookie of cookies) response.headers.append("set-cookie", cookie);
    return response;
  } catch {
    return NextResponse.json(
      {
        type: "https://system-news.example/problems/dependency-unavailable",
        title: "Dependency Unavailable",
        status: 503,
        detail: "The news API is temporarily unavailable.",
      },
      { status: 503 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const PUT = proxy;
