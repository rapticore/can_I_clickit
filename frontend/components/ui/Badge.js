const variants = {
  danger: "bg-red-100 text-danger",
  warning: "bg-amber-100 text-warning",
  safe: "bg-emerald-100 text-safe",
  neutral: "bg-slate-100 text-text-muted",
};

export default function Badge({ children, variant = "neutral", className = "" }) {
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-1 text-xs font-bold capitalize ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
