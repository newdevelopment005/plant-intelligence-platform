"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Leaf } from "lucide-react";

export default function VerifyEmail() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error" | "idle">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("idle");
      setMessage("Missing verification token.");
      return;
    }
    (async () => {
      try {
        const response = await fetch("/api/proxy/auth/verify-email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        });
        const data = await response.json().catch(() => ({ error: { message: "Server error" } }));
        if (!response.ok) {
          throw new Error(data.error?.message || data.detail || "Verification failed");
        }
        setStatus("success");
        setMessage(data.message || "Email verified successfully");
        setTimeout(() => router.push("/login?verified=true"), 2000);
      } catch (err) {
        setStatus("error");
        setMessage(err instanceof Error ? err.message : "An error occurred");
      }
    })();
  }, [token, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary/20 via-primary/10 to-background px-6">
      <div className="w-full max-w-md text-center space-y-6">
        <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2">
          <Leaf className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium text-primary">Plant Intelligence Platform</span>
        </div>
        {status === "loading" && (
          <>
            <div className="flex justify-center"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" /></div>
            <p className="text-muted-foreground">Verifying your email...</p>
          </>
        )}
        {status === "success" && (
          <>
            <h1 className="text-2xl font-bold">Email Verified</h1>
            <p className="text-green-600">{message}</p>
            <p className="text-sm text-muted-foreground">Redirecting to login...</p>
          </>
        )}
        {status === "error" && (
          <>
            <h1 className="text-2xl font-bold">Verification Failed</h1>
            <p className="text-destructive">{message}</p>
            <p className="text-sm text-muted-foreground">The link may have expired. You can request a new one from the login page.</p>
            <Link href="/login" className="inline-block rounded-md bg-primary px-4 py-2 text-white hover:bg-primary/90">Go to login</Link>
          </>
        )}
        {status === "idle" && (
          <>
            <h1 className="text-2xl font-bold">Missing Token</h1>
            <p className="text-muted-foreground">{message}</p>
            <Link href="/login" className="inline-block rounded-md bg-primary px-4 py-2 text-white hover:bg-primary/90">Go to login</Link>
          </>
        )}
      </div>
    </div>
  );
}