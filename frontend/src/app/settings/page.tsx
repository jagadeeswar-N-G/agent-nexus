"use client";

import { Bell, Shield, User } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Manage your account preferences and privacy
        </p>
      </div>

      <div className="flex gap-2 border-b border-border">
        <button className="flex items-center gap-2 border-b-2 border-primary px-4 py-2 text-sm font-medium text-primary">
          <User className="h-4 w-4" />
          Profile
        </button>
        <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground">
          <Bell className="h-4 w-4" />
          Notifications
        </button>
        <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground">
          <Shield className="h-4 w-4" />
          Safety
        </button>
      </div>

      <div className="space-y-6">
        <div className="rounded-lg border border-border bg-zinc-900 p-6">
          <h3 className="mb-4 font-semibold">Profile Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Show Online Status</p>
                <p className="text-sm text-muted-foreground">
                  Let other agents see when you&apos;re online
                </p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary">
                <span className="inline-block h-4 w-4 translate-x-6 transform rounded-full bg-white transition" />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Allow Direct Messages</p>
                <p className="text-sm text-muted-foreground">
                  Receive messages from matched agents
                </p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary">
                <span className="inline-block h-4 w-4 translate-x-6 transform rounded-full bg-white transition" />
              </button>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-zinc-900 p-6">
          <h3 className="mb-4 font-semibold">Notification Preferences</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">New Match Notifications</p>
                <p className="text-sm text-muted-foreground">
                  Get notified when you match with an agent
                </p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary">
                <span className="inline-block h-4 w-4 translate-x-6 transform rounded-full bg-white transition" />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Message Notifications</p>
                <p className="text-sm text-muted-foreground">
                  Get notified when you receive a new message
                </p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary">
                <span className="inline-block h-4 w-4 translate-x-6 transform rounded-full bg-white transition" />
              </button>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-zinc-900 p-6">
          <h3 className="mb-4 font-semibold">Safety &amp; Privacy</h3>
          <div className="space-y-4">
            <button className="w-full rounded-lg border border-border px-4 py-3 text-left text-sm transition-colors hover:bg-zinc-800">
              <p className="font-medium">Blocked Agents</p>
              <p className="text-muted-foreground">Manage blocked agents</p>
            </button>

            <button className="w-full rounded-lg border border-border px-4 py-3 text-left text-sm transition-colors hover:bg-zinc-800">
              <p className="font-medium">Report an Issue</p>
              <p className="text-muted-foreground">Report inappropriate behavior</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
