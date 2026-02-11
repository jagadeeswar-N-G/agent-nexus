"use client";

import { Toaster as SonnerToaster } from "sonner";

export function Toaster() {
  return (
    <SonnerToaster
      position="top-right"
      toastOptions={{
        style: {
          background: "hsl(240 5% 9%)",
          border: "1px solid hsl(240 3.7% 15.9%)",
          color: "hsl(0 0% 98%)",
        },
        className: "text-sm",
      }}
    />
  );
}
