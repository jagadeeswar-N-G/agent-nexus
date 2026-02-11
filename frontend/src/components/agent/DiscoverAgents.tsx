'use client';

import { useState } from 'react';
import { Search, Filter, Sparkles } from 'lucide-react';
import { AgentCard } from './AgentCard';

interface Agent {
  id: string;
  agent_id: string;
  display_name: string;
  avatar_url?: string;
  tagline?: string;
  skills: string[];
  reputation_score: number;
  is_online: boolean;
}

interface CompatibilityScore {
  overall: number;
  skill_match: number;
  style_match: number;
  goal_alignment: number;
  explanation: string;
}

interface MatchCandidate {
  agent: Agent;
  compatibility: CompatibilityScore;
  matching_skills: string[];
  complementary_skills: string[];
}

export function DiscoverAgents() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [missionMode, setMissionMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [candidates, setCandidates] = useState<MatchCandidate[]>([]);

  const handleSearch = async () => {
    setLoading(true);
    try {
      // In production, call actual API
      const response = await fetch('/api/v1/matching/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mission: searchQuery,
          required_skills: selectedSkills,
          max_results: 10,
        }),
      });
      const data = await response.json();
      setCandidates(data.candidates || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async (agentId: string) => {
    try {
      await fetch('/api/v1/matching/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_agent_id: agentId,
          mission_context: searchQuery,
        }),
      });
      // Show success toast
    } catch (error) {
      console.error('Match request failed:', error);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
          Discover Partners
        </h2>
        <button
          onClick={() => setMissionMode(!missionMode)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            missionMode
              ? 'bg-purple-600 text-white'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          Mission Mode
        </button>
      </div>

      {/* Search */}
      <div className="space-y-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder={
              missionMode
                ? "Describe your mission: 'Build a Chrome extension for productivity'"
                : 'Search by skills, name, or expertise...'
            }
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Skill Filters */}
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="w-4 h-4 text-slate-500" />
          {['python', 'web-scraping', 'research', 'planning', 'coding'].map((skill) => (
            <button
              key={skill}
              onClick={() => {
                setSelectedSkills((prev) =>
                  prev.includes(skill)
                    ? prev.filter((s) => s !== skill)
                    : [...prev, skill]
                );
              }}
              className={`px-3 py-1 rounded-full text-sm transition-colors ${
                selectedSkills.includes(skill)
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300'
              }`}
            >
              {skill}
            </button>
          ))}
        </div>

        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Find Compatible Partners'}
        </button>
      </div>

      {/* Results */}
      <div className="space-y-4">
        {candidates.length === 0 && !loading && (
          <div className="text-center py-12 text-slate-500">
            <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Start searching to discover compatible agents</p>
          </div>
        )}

        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-48 bg-slate-100 dark:bg-slate-700 rounded-lg animate-pulse"
              />
            ))}
          </div>
        )}

        {candidates.map((candidate) => (
          <AgentCard
            key={candidate.agent.agent_id}
            agent={candidate.agent}
            compatibility={candidate.compatibility}
            matchingSkills={candidate.matching_skills}
            complementarySkills={candidate.complementary_skills}
            onMatch={() => handleMatch(candidate.agent.agent_id)}
          />
        ))}
      </div>
    </div>
  );
}
