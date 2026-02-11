import { HTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";
import { getInitials, getAvatarGradient } from "@/lib/theme";

export interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  name?: string;
  index?: number;
  size?: "sm" | "md" | "lg" | "xl";
}

const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, src, alt, name, index = 0, size = "md", ...props }, ref) => {
    const sizes = {
      sm: "h-8 w-8 text-xs",
      md: "h-10 w-10 text-sm",
      lg: "h-16 w-16 text-lg",
      xl: "h-24 w-24 text-2xl",
    };

    const gradientClass = getAvatarGradient(index);
    const initials = name ? getInitials(name) : "?";

    if (src) {
      return (
        <div
          ref={ref}
          className={cn(
            "relative flex shrink-0 items-center justify-center overflow-hidden rounded-full",
            sizes[size],
            className
          )}
          {...props}
        >
          <img src={src} alt={alt || name || "Avatar"} className="h-full w-full object-cover" />
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={cn(
          "flex shrink-0 items-center justify-center rounded-full font-bold text-white",
          gradientClass,
          sizes[size],
          className
        )}
        {...props}
      >
        {initials}
      </div>
    );
  }
);

Avatar.displayName = "Avatar";

export { Avatar };
