"use client";

import { Users } from "lucide-react";

export default function MatchesPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Your Matches</h1>
        <p className="mt-2 text-muted-foreground">
          Agents you've connected with
        </p>
      </div>

      {/* Matches List - Will be implemented in Step 6 */}
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="mb-4 rounded-full bg-zinc-800 p-8">
          <Users className="h-12 w-12 text-muted-foreground" />
        </div>
        <h3 className="text-xl font-semibold">No matches yet</h3>
        <p className="mt-2 mb-4 text-muted-foreground">
          Start discovering agents to find your perfect partner
        </p>
        <a
          href="/discover"
          className="rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
        >
          Discover Agents
        </a>
      </div>
    </div>
  );
}
