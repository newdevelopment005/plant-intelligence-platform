import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PREFIXES = [
  "/dashboard",
  "/ai",
  "/projects",
  "/germplasm",
  "/phenotyping",
  "/genomics",
  "/molecular",
  "/literature",
  "/knowledge-graph",
  "/notebook",
  "/lims",
  "/images",
  "/reports",
  "/teams",
  "/shared",
  "/meetings",
  "/admin",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/api/")) {
    return NextResponse.next();
  }

  const isProtected = PROTECTED_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  );

  if (isProtected) {
    const hasSession =
      request.cookies.get("pip_session")?.value === "1" ||
      request.headers.get("x-pip-session") === "1";

    if (!hasSession) {
      const loginUrl = request.nextUrl.clone();
      loginUrl.pathname = "/login";
      loginUrl.searchParams.set("from", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};