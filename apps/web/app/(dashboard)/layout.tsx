import Link from "next/link";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/projects", label: "Projects" },
  { href: "/germplasm", label: "Germplasm" },
  { href: "/phenotyping", label: "Phenotyping" },
  { href: "/genomics", label: "Genomics" },
  { href: "/molecular", label: "Molecular" },
  { href: "/literature", label: "Literature" },
  { href: "/knowledge-graph", label: "Knowledge Graph" },
  { href: "/notebook", label: "Notebook" },
  { href: "/lims", label: "LIMS" },
  { href: "/images", label: "Images" },
  { href: "/reports", label: "Reports" },
  { href: "/admin", label: "Admin" },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r bg-muted/40 p-4">
        <div className="mb-8">
          <h1 className="text-lg font-bold">PIP</h1>
          <p className="text-xs text-muted-foreground">Plant Intelligence Platform</p>
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
