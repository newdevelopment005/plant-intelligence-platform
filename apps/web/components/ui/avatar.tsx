import { cn } from "@/lib/utils";

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  fallback?: string;
}

function Avatar({ className, src, alt, fallback, children, ...props }: AvatarProps) {
  if (src) {
    return (
      <div className={cn("relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full", className)} {...props}>
        <img src={src} alt={alt || ""} className="aspect-square h-full w-full" />
      </div>
    );
  }
  return (
    <div className={cn("relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full", className)} {...props}>
      {children || (
        <div className="flex h-full w-full items-center justify-center rounded-full bg-muted text-sm font-medium">
          {fallback || "?"}
        </div>
      )}
    </div>
  );
}

function AvatarFallback({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("flex h-full w-full items-center justify-center rounded-full bg-muted text-sm font-medium", className)} {...props}>
      {children}
    </div>
  );
}

export { Avatar, AvatarFallback };
