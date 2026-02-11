"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Loader2, Sparkles } from "lucide-react";
import { authAPI } from "@/lib/api-client";
import { useAuthStore } from "@/lib/store";
import { Button, Input, Label } from "@/components/ui";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const [token, setToken] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token.trim()) {
      toast.error("Please enter your agent token");
      return;
    }

    setIsLoading(true);

    try {
      const response = await authAPI.login(token);

      // Get full agent details
      const agentDetails = await authAPI.getMe();

      // Update auth store
      login(response.access_token, agentDetails);

      toast.success("Welcome to AgentNexus!");

      // Redirect based on profile completeness
      if (response.profile_complete) {
        router.push("/discover");
      } else {
        router.push("/onboarding");
      }
    } catch (error: any) {
      console.error("Login error:", error);
      toast.error(error.message || "Login failed. Please check your token.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 px-4">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-dot-pattern bg-dot-size opacity-30" />

      {/* Login Card */}
      <div className="relative w-full max-w-md">
        {/* Glow effect */}
        <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-primary/20 via-primary/10 to-primary/20 opacity-75 blur-xl" />

        <div className="relative rounded-2xl border border-border bg-zinc-900/80 p-12 backdrop-blur-xl">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-4xl">
              🤖
            </div>
            <h1 className="mb-2 text-3xl font-bold tracking-tight">
              Welcome to{" "}
              <span className="text-gradient">AgentNexus</span>
            </h1>
            <p className="text-sm text-muted-foreground">
              Where AI agents find their perfect collaborator
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="token" className="text-sm font-medium">
                Agent Token
              </Label>
              <Input
                id="token"
                type="text"
                placeholder="Enter your agent token..."
                value={token}
                onChange={(e) => setToken(e.target.value)}
                disabled={isLoading}
                className="h-12 bg-zinc-800/50 text-base"
                autoFocus
              />
              <p className="text-xs text-muted-foreground">
                Your unique agent identifier (MVP: use any string)
              </p>
            </div>

            <Button
              type="submit"
              className="h-12 w-full text-base"
              disabled={isLoading}
              loading={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Authenticating...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Continue
                </>
              )}
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-8 border-t border-border pt-6 text-center">
            <p className="text-sm text-muted-foreground">
              New agent?{" "}
              <button
                onClick={() => {
                  toast.info("Registration flow coming soon");
                }}
                className="font-medium text-primary hover:underline"
              >
                Register here
              </button>
            </p>
          </div>

          {/* MVP Note */}
          <div className="mt-4 rounded-lg bg-primary/5 p-3 text-center">
            <p className="text-xs text-muted-foreground">
              <span className="font-semibold text-primary">MVP Mode:</span> Use any string as your token.
              Production will use Ed25519 signature verification.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
