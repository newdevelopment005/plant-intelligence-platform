import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const filePath = path.join("/");

  try {
    const backendResponse = await fetch(`${BACKEND_URL}/storage/${filePath}`, {
      headers: { "ngrok-skip-browser-warning": "true" },
    });

    if (!backendResponse.ok) {
      return new NextResponse("Image not found", { status: 404 });
    }

    const contentType = backendResponse.headers.get("content-type") || "application/octet-stream";
    const body = await backendResponse.arrayBuffer();

    return new NextResponse(body, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=86400",
      },
    });
  } catch {
    return new NextResponse("Failed to fetch image", { status: 500 });
  }
}
