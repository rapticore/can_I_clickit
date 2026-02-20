import "./globals.css";

export const metadata = {
  title: "Can I Click It? Web Tester",
  description: "Local test console for Can I Click It scan API",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
