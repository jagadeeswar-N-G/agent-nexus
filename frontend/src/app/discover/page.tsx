"use client";

import { useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";

export default function DiscoverPage() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Discover Agents</h1>
        <p className="mt-2 text-muted-foreground">
          Find your perfect collaboration partner
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by skills, name, or mission..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-border bg-zinc-800 py-3 pl-11 pr-4 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <button className="flex items-center gap-2 rounded-lg border border-border bg-zinc-900 px-4 py-3 text-sm font-medium transition-colors hover:bg-zinc-800">
          <SlidersHorizontal className="h-4 w-4" />
          Filters
        </button>
      </div>

      {/* Agent Cards Grid - Will be implemented in Step 5 */}
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="mb-4 rounded-full bg-zinc-800 p-8">
          <Search className="h-12 w-12 text-muted-foreground" />
        </div>
        <h3 className="text-xl font-semibold">Start discovering</h3>
        <p className="mt-2 text-muted-foreground">
          Search or browse to find compatible agents
        </p>
      </div>
    </div>
  );
}
