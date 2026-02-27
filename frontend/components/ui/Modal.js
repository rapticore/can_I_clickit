"use client";

import { useEffect, useRef } from "react";

export default function Modal({ open, onClose, title, children }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open) {
      dialog.showModal();
    } else {
      dialog.close();
    }
  }, [open]);

  return (
    <dialog
      ref={dialogRef}
      onClose={onClose}
      className="fixed inset-0 z-50 m-auto max-w-lg w-[calc(100%-2rem)] rounded-2xl border border-card-edge bg-card p-6 shadow-xl backdrop:bg-black/40 backdrop:backdrop-blur-sm"
    >
      {title && (
        <h2 className="text-lg font-bold text-text-primary mb-4">{title}</h2>
      )}
      {children}
    </dialog>
  );
}
