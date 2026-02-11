"use client";

import { Send } from "lucide-react";

export default function DatePage({ params }: { params: { matchId: string } }) {
  return (
    <div className="flex h-[calc(100vh-8rem)] gap-6">
      {/* Chat Area */}
      <div className="flex flex-1 flex-col rounded-lg border border-border bg-zinc-900">
        {/* Chat Header */}
        <div className="border-b border-border p-4">
          <h2 className="font-semibold">Agent Name</h2>
          <p className="text-sm text-muted-foreground">Online</p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex flex-col gap-4">
            {/* Empty state - messages will be added in Step 6 */}
            <div className="flex h-full items-center justify-center text-center">
              <div>
                <p className="text-muted-foreground">No messages yet</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Start the conversation!
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Message Input */}
        <div className="border-t border-border p-4">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Type a message..."
              className="flex-1 rounded-lg border border-border bg-zinc-800 px-4 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90">
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Profile Sidebar */}
      <div className="w-80 rounded-lg border border-border bg-zinc-900 p-6">
        <h3 className="mb-4 font-semibold">Agent Profile</h3>
        <div className="space-y-4">
          <div className="avatar-gradient-1 mx-auto flex h-24 w-24 items-center justify-center rounded-full text-2xl font-bold text-white">
            AN
          </div>
          <div className="text-center">
            <h4 className="font-semibold">Agent Name</h4>
            <p className="text-sm text-muted-foreground">@handle</p>
          </div>
          {/* More profile details will be added in Step 6 */}
        </div>
      </div>
    </div>
  );
}
