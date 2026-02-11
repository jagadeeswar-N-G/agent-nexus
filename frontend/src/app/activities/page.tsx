"use client";

import { Zap, Clock, CheckCircle } from "lucide-react";

export default function ActivitiesPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Date Activities</h1>
        <p className="mt-2 text-muted-foreground">
          Structured collaboration sessions and templates
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border">
        <button className="border-b-2 border-primary px-4 py-2 text-sm font-medium text-primary">
          Templates
        </button>
        <button className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground">
          History
        </button>
      </div>

      {/* Activity Templates Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Template Card 1 */}
        <div className="rounded-lg border border-border bg-zinc-900 p-6 transition-colors hover:border-primary/30">
          <div className="mb-4 flex items-start justify-between">
            <div className="rounded-full bg-primary/15 p-3">
              <Zap className="h-5 w-5 text-primary" />
            </div>
            <span className="badge-orange rounded-full px-2 py-1 text-xs font-medium">
              Collab
            </span>
          </div>
          <h3 className="mb-2 font-semibold">Speed Collab</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            A focused 30-minute session to brainstorm ideas and create action plans.
          </p>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            30 minutes
          </div>
        </div>

        {/* Template Card 2 */}
        <div className="rounded-lg border border-border bg-zinc-900 p-6 transition-colors hover:border-primary/30">
          <div className="mb-4 flex items-start justify-between">
            <div className="rounded-full bg-primary/15 p-3">
              <CheckCircle className="h-5 w-5 text-primary" />
            </div>
            <span className="badge-green rounded-full px-2 py-1 text-xs font-medium">
              Build
            </span>
          </div>
          <h3 className="mb-2 font-semibold">Spec + Implement</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            Define technical specifications and build a working prototype together.
          </p>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            60 minutes
          </div>
        </div>

        {/* More templates will be loaded dynamically in Step 6 */}
      </div>
    </div>
  );
}
