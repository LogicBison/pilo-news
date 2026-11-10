import { NextResponse } from "next/server";

// The API owns the count and the redirect target; this route exists because the
// reader must stay on the article's own host until the last moment. No reader
// identifier is added here: the API counts one click against one article.
const API_BASE = process.env.API_INTERNAL_URL ?? "http://api:8080";

export const dynamic = "force-dynamic";

export async function GET(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  try {
    const upstream = await fetch(
      `${API_BASE.replace(/\/$/, "")}/v1/outbound/${encodeURIComponent(id)}`,
      { redirect: "manual", cache: "no-store" },
    );
    const location = upstream.headers.get("location");
    if (upstream.status >= 300 && upstream.status < 400 && location) {
      return NextResponse.redirect(location, 302);
    }
  } catch {
    // fall through to the channel home
  }
  return NextResponse.redirect(new URL("/", request.url), 302);
}
