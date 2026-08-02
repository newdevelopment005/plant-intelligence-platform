import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold">Plant Intelligence Platform</h1>
      </div>

      <div className="mt-32 grid text-center lg:max-w-5xl lg:w-full lg:mb-0 lg:grid-cols-3 gap-8">
        <Link
          href="/login"
          className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100"
        >
          <h2 className="mb-3 text-2xl font-semibold">Login</h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Sign in to access your research platform.
          </p>
        </Link>

        <Link
          href="/register"
          className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100"
        >
          <h2 className="mb-3 text-2xl font-semibold">Register</h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Create an account to get started.
          </p>
        </Link>

        <Link
          href="/dashboard"
          className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100"
        >
          <h2 className="mb-3 text-2xl font-semibold">Dashboard</h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Access your research dashboard.
          </p>
        </Link>
      </div>
    </main>
  );
}
