import { HTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "orange" | "green" | "blue" | "purple";
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = "default", ...props }, ref) => {
    const variants = {
      default: "bg-zinc-800 text-foreground",
      orange: "badge-orange",
      green: "badge-green",
      blue: "bg-blue-500/15 text-blue-400 border border-blue-500/30",
      purple: "bg-purple-500/15 text-purple-400 border border-purple-500/30",
    };

    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium",
          variants[variant],
          className
        )}
        {...props}
      />
    );
  }
);

Badge.displayName = "Badge";

export { Badge };
