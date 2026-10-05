/**
 * Clerk Provider Template
 *
 * Place this at: frontend/apps/dashboard/providers/clerk-provider.tsx
 */

"use client";

import { ClerkProvider as BaseClerkProvider } from "@clerk/nextjs";
import { dark } from "@clerk/themes";

interface ClerkProviderProps {
  children: React.ReactNode;
}

export function ClerkProvider({ children }: ClerkProviderProps) {
  return (
    <BaseClerkProvider
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: "#3b82f6",
          colorBackground: "#0f172a",
          colorInputBackground: "#1e293b",
          colorInputText: "#f8fafc",
        },
        elements: {
          formButtonPrimary:
            "bg-blue-600 hover:bg-blue-700 text-white font-medium",
          card: "bg-slate-900 border border-slate-800",
          headerTitle: "text-white",
          headerSubtitle: "text-slate-400",
          socialButtonsBlockButton:
            "bg-slate-800 border-slate-700 text-white hover:bg-slate-700",
          formFieldLabel: "text-slate-300",
          formFieldInput: "bg-slate-800 border-slate-700 text-white",
          footerActionLink: "text-blue-500 hover:text-blue-400",
        },
      }}
    >
      {children}
    </BaseClerkProvider>
  );
}
