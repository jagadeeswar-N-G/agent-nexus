"use client";

export function QuickActions() {
  return (
    <div className="rounded-lg border bg-card p-6">
      <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
      <div className="space-y-2">
        <button className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90">
          Find Agents
        </button>
        <button className="w-full px-4 py-2 border rounded-md hover:bg-accent">
          View Profile
        </button>
      </div>
    </div>
  );
}
