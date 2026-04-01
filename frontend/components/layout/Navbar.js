"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "lib/auth-context";
import { useUXMode } from "lib/ux-mode-context";

const navLinks = [
  { href: "/dashboard", label: "Dashboard", icon: "\uD83D\uDD0D" },
  { href: "/history", label: "History", icon: "\uD83D\uDCCB" },
  { href: "/recovery", label: "Recovery", icon: "\uD83D\uDEE1\uFE0F" },
  { href: "/settings", label: "Settings", icon: "\u2699\uFE0F" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const { isGrandmaMode } = useUXMode();
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-40 border-b border-card-edge bg-card/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link
          href="/dashboard"
          className={`font-bold no-underline hover:no-underline text-text-primary ${isGrandmaMode ? "text-xl" : "text-lg"}`}
        >
          Can I Click It?
        </Link>

        {/* Desktop nav */}
        <div className="hidden items-center gap-1 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-lg px-3 py-2 no-underline hover:no-underline transition-colors ${
                isGrandmaMode ? "text-base" : "text-sm"
              } ${
                pathname === link.href
                  ? "bg-brand/10 text-brand font-semibold"
                  : "text-text-muted hover:bg-bg-base hover:text-text-primary"
              }`}
            >
              {isGrandmaMode && <span className="mr-1.5">{link.icon}</span>}
              {link.label}
            </Link>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          {user && (
            <>
              <span className={`text-text-muted ${isGrandmaMode ? "text-base" : "text-sm"}`}>
                {user.email}
              </span>
              <button
                onClick={logout}
                className={`rounded-lg border border-card-edge px-3 py-1.5 text-text-muted hover:bg-bg-base transition-colors cursor-pointer ${
                  isGrandmaMode ? "text-base" : "text-sm"
                }`}
              >
                Log out
              </button>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="flex flex-col gap-1 p-2 md:hidden cursor-pointer"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          <span className={`block h-0.5 w-5 bg-text-primary transition-transform ${menuOpen ? "translate-y-1.5 rotate-45" : ""}`} />
          <span className={`block h-0.5 w-5 bg-text-primary transition-opacity ${menuOpen ? "opacity-0" : ""}`} />
          <span className={`block h-0.5 w-5 bg-text-primary transition-transform ${menuOpen ? "-translate-y-1.5 -rotate-45" : ""}`} />
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="border-t border-card-edge px-4 pb-4 md:hidden">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMenuOpen(false)}
              className={`block rounded-lg px-3 py-2.5 text-base no-underline hover:no-underline transition-colors ${
                pathname === link.href
                  ? "bg-brand/10 text-brand font-semibold"
                  : "text-text-muted hover:bg-bg-base"
              }`}
            >
              <span className="mr-2">{link.icon}</span>
              {link.label}
            </Link>
          ))}
          {user && (
            <button
              onClick={() => {
                setMenuOpen(false);
                logout();
              }}
              className="mt-2 w-full rounded-lg border border-card-edge px-3 py-2.5 text-base text-text-muted hover:bg-bg-base cursor-pointer text-left"
            >
              Log out ({user.email})
            </button>
          )}
        </div>
      )}
    </nav>
  );
}
