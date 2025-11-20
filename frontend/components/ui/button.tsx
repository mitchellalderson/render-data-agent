import * as React from "react";
import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "icon" | "xs";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const base =
      "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-500 disabled:opacity-50 disabled:pointer-events-none";
    const variants: Record<string, string> = {
      default: "bg-zinc-100 text-black hover:bg-zinc-200",
      outline:
        "border border-zinc-800 bg-transparent text-zinc-100 hover:bg-zinc-900",
      ghost: "bg-transparent text-zinc-300 hover:bg-zinc-900"
    };
    const sizes: Record<string, string> = {
      default: "h-9 px-3",
      icon: "h-9 w-9",
      xs: "h-6 px-2 text-xs"
    };
    return (
      <button
        ref={ref}
        className={cn(base, variants[variant], sizes[size], className)}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";
