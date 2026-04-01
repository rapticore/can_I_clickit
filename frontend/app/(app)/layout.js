"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "lib/auth-context";
import Navbar from "components/layout/Navbar";
import Footer from "components/layout/Footer";
import Spinner from "components/ui/Spinner";

export default function AppLayout({ children }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
        {children}
      </main>
      <Footer />
    </div>
  );
}
