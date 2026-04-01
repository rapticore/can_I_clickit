"use client";

import Spinner from "./Spinner";

const variants = {
  primary:
    "bg-gradient-to-br from-brand to-brand-light text-white hover:opacity-90",
  secondary:
    "border border-card-edge bg-card text-text-primary hover:bg-bg-base",
  danger:
    "bg-danger text-white hover:opacity-90",
  ghost:
    "bg-transparent text-text-muted hover:bg-bg-base",
};

const sizes = {
  sm: "px-3 py-1.5 text-sm rounded-lg",
  md: "px-4 py-2.5 text-sm rounded-xl",
  lg: "px-6 py-3 text-base rounded-xl",
};

export default function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  className = "",
  ...props
}) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 font-semibold transition-all cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed focus:outline-2 focus:outline-offset-2 focus:outline-brand ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
}
