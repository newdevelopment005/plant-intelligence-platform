"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Leaf } from "lucide-react";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        `/api/proxy/auth/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        }
      );

      const data = await response.json().catch(() => ({ error: { message: "Server error" } }));

      if (!response.ok) {
        throw new Error(data.error?.message || data.detail || "Login failed");
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      document.cookie = "pip_session=1; path=/; SameSite=Lax";

      const from = new URLSearchParams(window.location.search).get("from");
      router.push(from || "/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left side - branding */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-primary/20 via-primary/10 to-background items-center justify-center">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-primary/10 to-background" />
        <div className="relative z-10 max-w-md px-8 text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2">
            <Leaf className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium text-primary">Plant Intelligence Platform</span>
          </div>
          <h2 className="mb-4 text-3xl font-bold">AI-Powered Plant Research</h2>
          <p className="text-muted-foreground">
            Manage germplasm, run experiments, analyze genomics, and chat with a local AI assistant.
            Zero API costs. Full privacy.
          </p>
        </div>
      </div>

      {/* Right side - form */}
      <div className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile logo */}
          <div className="lg:hidden text-center">
            <div className="mb-4 inline-flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary">
                <Leaf className="h-6 w-6 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">PIP</span>
            </div>
          </div>

          <div>
            <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Sign in to your research platform
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="researcher@lab.org"
                className="h-11"
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Link href="/forgot-password" className="text-xs text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="h-11"
              />
            </div>

            <Button type="submit" disabled={loading} className="w-full h-11">
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="font-medium text-primary hover:underline">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
