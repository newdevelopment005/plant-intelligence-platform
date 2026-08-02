export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <h2 className="text-4xl font-bold mb-4">404</h2>
      <p className="text-xl text-muted-foreground mb-8">Page not found</p>
      <a
        href="/"
        className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
      >
        Go home
      </a>
    </div>
  );
}
