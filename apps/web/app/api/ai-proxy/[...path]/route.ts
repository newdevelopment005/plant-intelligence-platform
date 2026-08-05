import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  (process.env.BACKEND_URL || "https://uniquely-buggy-whomever.ngrok-free.dev").replace(/\/$/, "");

async function proxyRequest(request: NextRequest, path: string) {
  const url = `${BACKEND_URL}/ai-proxy/${path}`;

  const headers: Record<string, string> = {
    "Content-Type": request.headers.get("content-type") || "application/json",
    "ngrok-skip-browser-warning": "true",
  };

  const auth = request.headers.get("authorization");
  if (auth) {
    headers["Authorization"] = auth;
  }

  const body =
    request.method !== "GET" && request.method !== "HEAD"
      ? await request.arrayBuffer()
      : undefined;

  try {
    const response = await fetch(url, {
      method: request.method,
      headers,
      body,
      signal: AbortSignal.timeout(120000),
    });

    return new NextResponse(response.body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("content-type") || "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Proxy request failed" },
      { status: 502 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path.join("/"));
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path.join("/"));
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path.join("/"));
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path.join("/"));
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type,Authorization",
    },
  });
}
