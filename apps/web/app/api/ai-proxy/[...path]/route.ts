import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1").replace(
    /\/api\/v1$/,
    ""
  );

async function proxyRequest(request: NextRequest, path: string) {
  const url = `${BACKEND_URL}/ai-proxy/${path}`;
  const headers = new Headers();

  request.headers.forEach((value, key) => {
    if (key.toLowerCase() !== "host" && key.toLowerCase() !== "connection") {
      headers.set(key, value);
    }
  });

  headers.set("ngrok-skip-browser-warning", "true");

  const body =
    request.method !== "GET" && request.method !== "HEAD"
      ? await request.arrayBuffer()
      : undefined;

  const response = await fetch(url, {
    method: request.method,
    headers,
    body,
    signal: AbortSignal.timeout(120000),
  });

  const responseHeaders = new Headers();
  responseHeaders.set(
    "Content-Type",
    response.headers.get("content-type") || "application/json"
  );
  responseHeaders.set("Access-Control-Allow-Origin", "*");

  return new NextResponse(response.body, {
    status: response.status,
    headers: responseHeaders,
  });
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
