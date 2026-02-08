"use client";

import React, { createContext, useContext, useState, useCallback } from "react";

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: "default" | "destructive";
}

interface ToastContextType {
  toast: (toast: Omit<Toast, "id">) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback(({ title, description, variant = "default" }: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, title, description, variant }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`p-4 rounded-lg shadow-lg border min-w-[300px] animate-in slide-in-from-right-full ${
              t.variant === "destructive"
                ? "bg-red-600 text-white border-red-700"
                : "bg-white text-gray-900 border-gray-200"
            }`}
          >
            <div className="font-bold">{t.title}</div>
            {t.description && <div className="text-sm opacity-90">{t.description}</div>}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
