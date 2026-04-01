import "./globals.css";
import { AuthProvider } from "lib/auth-context";
import { UXModeProvider } from "lib/ux-mode-context";

export const metadata = {
  title: "Can I Click It?",
  description: "AI-Powered Personal Safety Assistant — A Seatbelt for the Internet",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen text-text-primary antialiased">
        <AuthProvider>
          <UXModeProvider>{children}</UXModeProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
