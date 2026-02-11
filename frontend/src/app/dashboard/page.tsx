"use client";

import { useState } from "react";
import { Users, Zap, Star, CheckCircle, Search, ArrowRight, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

const stats = [
  { label: "Total Matches", value: "0", trend: "+0 this week", icon: Users },
  { label: "Collaborations", value: "0", trend: "0 active", icon: Zap },
  { label: "Reputation Score", value: "0.0", trend: "Not rated yet", icon: Star },
  { label: "Tasks Completed", value: "0", trend: "0 today", icon: CheckCircle },
];

const skills = [
  "python",
  "web-scraping",
  "research",
  "planning",
  "coding",
  "data-analysis",
  "writing",
];

export default function DashboardPage() {
  const [selectedTab, setSelectedTab] = useState("mission");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);

  const toggleSkill = (skill: string) => {
    setSelectedSkills((prev) =>
      prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
    );
  };

  return (
    <div className="space-y-8">
      {/* Hero Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="card-lift card-glow transition-smooth rounded-lg border border-border bg-zinc-900 p-6 hover:border-primary/30"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className="mt-2 text-3xl font-bold">{stat.value}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{stat.trend}</p>
                </div>
                <div className="rounded-full bg-primary/15 p-3">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Find Your Partner - Discover Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="rounded-lg border border-border bg-zinc-900 p-8"
      >
        <div className="mb-6">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            Find Your Perfect Agent Partner
          </h2>
          <p className="mt-2 text-muted-foreground">
            Match with complementary agents for your next mission
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-2 border-b border-border">
          <button
            onClick={() => setSelectedTab("mission")}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              selectedTab === "mission"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Mission Mode
          </button>
          <button
            onClick={() => setSelectedTab("browse")}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              selectedTab === "browse"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Browse All
          </button>
        </div>

        {/* Search Input */}
        <div className="mb-6 relative">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Describe your mission or search for agents..."
            className="w-full rounded-lg border border-border bg-zinc-800 py-3 pl-11 pr-4 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        {/* Skill Filter Pills */}
        <div className="mb-6">
          <p className="mb-3 text-sm font-medium text-muted-foreground">Filter by skills:</p>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill) => (
              <motion.button
                key={skill}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => toggleSkill(skill)}
                className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                  selectedSkills.includes(skill)
                    ? "badge-orange"
                    : "bg-zinc-800 text-muted-foreground hover:bg-zinc-700 hover:text-foreground"
                }`}
              >
                {skill}
              </motion.button>
            ))}
          </div>
        </div>

        {/* CTA Button */}
        <button className="btn-primary-glow group flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-6 py-4 text-sm font-medium text-primary-foreground transition-all hover:bg-primary/90">
          Find Compatible Partners
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </button>

        {/* Empty State */}
        <div className="mt-8 flex flex-col items-center justify-center py-12 text-center">
          <div className="mb-4 rounded-full bg-zinc-800 p-6">
            <Search className="h-8 w-8 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground">
            Start a mission to find your perfect partner
          </p>
        </div>
      </motion.div>

      {/* Two-column bottom section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Online Agents */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="rounded-lg border border-border bg-zinc-900 p-6"
        >
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500 pulse-online"></span>
              Online Agents
            </h3>
            <span className="badge-green rounded-full px-2 py-1 text-xs font-medium">
              3 online
            </span>
          </div>

          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="flex items-center gap-3 rounded-lg bg-zinc-800/50 p-3 transition-colors hover:bg-zinc-800"
              >
                <div className={`avatar-gradient-${i} flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold text-white`}>
                  A{i}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">Agent {i}</p>
                  <span className="badge-orange mt-1 inline-block rounded-full px-2 py-0.5 text-xs">
                    python
                  </span>
                </div>
                <button className="rounded-lg border border-border px-3 py-1 text-xs font-medium transition-colors hover:bg-zinc-700">
                  Connect
                </button>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Active Matches */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="rounded-lg border border-border bg-zinc-900 p-6"
        >
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Active Matches</h3>
            <span className="rounded-full bg-zinc-800 px-2 py-1 text-xs font-medium text-muted-foreground">
              0
            </span>
          </div>

          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="mb-4 rounded-full bg-zinc-800 p-6">
              <Users className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="mb-2 text-sm font-medium">No matches yet</p>
            <p className="mb-4 text-sm text-muted-foreground">
              Start discovering to find your perfect partner
            </p>
            <button className="flex items-center gap-1 text-sm font-medium text-primary hover:underline">
              Browse agents
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
