"use client";

export default function Input({
  label,
  error,
  type = "text",
  className = "",
  id,
  ...props
}) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");
  const isTextarea = type === "textarea";
  const Tag = isTextarea ? "textarea" : "input";

  return (
    <div className={`grid gap-1.5 ${className}`}>
      {label && (
        <label
          htmlFor={inputId}
          className="text-sm font-medium text-text-muted"
        >
          {label}
        </label>
      )}
      <Tag
        id={inputId}
        type={isTextarea ? undefined : type}
        className={`w-full rounded-xl border px-3 py-2.5 text-text-primary bg-white transition-colors focus:outline-none focus:ring-2 focus:ring-brand/40 ${
          error
            ? "border-danger focus:ring-danger/40"
            : "border-card-edge"
        } ${isTextarea ? "min-h-[120px] resize-y" : ""}`}
        aria-invalid={error ? "true" : undefined}
        aria-describedby={error ? `${inputId}-error` : undefined}
        {...props}
      />
      {error && (
        <p id={`${inputId}-error`} className="text-sm text-danger font-medium" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
