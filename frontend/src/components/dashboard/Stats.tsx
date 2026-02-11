"use client";

export function Stats() {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <div className="rounded-lg border bg-card p-6">
        <div className="text-sm text-muted-foreground">Total Matches</div>
        <div className="text-3xl font-bold">0</div>
      </div>
      <div className="rounded-lg border bg-card p-6">
        <div className="text-sm text-muted-foreground">Collaborations</div>
        <div className="text-3xl font-bold">0</div>
      </div>
      <div className="rounded-lg border bg-card p-6">
        <div className="text-sm text-muted-foreground">Reputation</div>
        <div className="text-3xl font-bold">0</div>
      </div>
    </div>
  );
}
