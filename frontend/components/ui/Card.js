export default function Card({ children, className = "", ...props }) {
  return (
    <div
      className={`rounded-2xl border border-card-edge bg-card shadow-lg p-4 sm:p-6 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
