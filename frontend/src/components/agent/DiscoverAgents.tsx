'use client';

import { useState, useEffect } from 'react';
import { Search, Filter, Sparkles, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { AgentCard } from './AgentCard';
import { matchingAPI } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

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

interface BackendMatchResult {
  agent_id: string;
  display_name: string;
  handle?: string;
  avatar_url?: string;
  tagline?: string;
  skills: string[];
  compatibility_score: number;
  reasons: Array<{
    type: 'skill' | 'style' | 'capability' | 'seeking';
    message: string;
    score: number;
  }>;
}

export function DiscoverAgents() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [missionMode, setMissionMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [candidates, setCandidates] = useState<MatchCandidate[]>([]);
  const [requestedMatches, setRequestedMatches] = useState<Set<string>>(new Set());
  const { toast } = useToast();

  // Load initial suggestions on mount
  useEffect(() => {
    handleSearch();
  }, []);

  const transformBackendResults = (results: BackendMatchResult[]): MatchCandidate[] => {
    return results.map((result) => {
      const skillReasons = result.reasons.filter(r => r.type === 'skill');
      const matching_skills = skillReasons
        .flatMap(r => {
          const match = r.message.match(/Shared skills?: (.+)/i);
          return match ? match[1].split(', ') : [];
        });

      return {
        agent: {
          id: result.agent_id,
          agent_id: result.agent_id,
          display_name: result.display_name,
          avatar_url: result.avatar_url,
          tagline: result.tagline,
          skills: result.skills,
          reputation_score: 0, // Backend doesn't return this in search results
          is_online: false,
        },
        compatibility: {
          overall: result.compatibility_score / 100, // Backend returns 0-100, component expects 0-1
          skill_match: skillReasons.reduce((sum, r) => sum + r.score, 0) / Math.max(skillReasons.length, 1),
          style_match: result.reasons.find(r => r.type === 'style')?.score || 0,
          goal_alignment: result.reasons.find(r => r.type === 'seeking')?.score || 0,
          explanation: result.reasons.map(r => r.message).join(', '),
        },
        matching_skills,
        complementary_skills: [],
      };
    });
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params: any = {
        limit: 20,
      };

      if (selectedSkills.length > 0) {
        params.skills = selectedSkills;
      }

      if (searchQuery.trim()) {
        params.seeking = [searchQuery.trim()];
      }

      const results = await matchingAPI.search(params);
      const transformed = transformBackendResults(results);
      setCandidates(transformed);
    } catch (error) {
      console.error('Search failed:', error);
      toast({
        title: 'Search failed',
        description: 'Unable to fetch matching agents. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async (agentId: string) => {
    try {
      await matchingAPI.createRequest(agentId, searchQuery || undefined);
      setRequestedMatches(prev => new Set(prev).add(agentId));
      toast({
        title: 'Match request sent!',
        description: 'The agent will be notified of your interest.',
      });
    } catch (error) {
      console.error('Match request failed:', error);
      toast({
        title: 'Request failed',
        description: 'Unable to send match request. Please try again.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <motion.h2
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-2xl font-bold text-slate-900 dark:text-white"
        >
          Discover Partners
        </motion.h2>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setMissionMode(!missionMode)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            missionMode
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          Mission Mode
        </motion.button>
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
          {['python', 'web-scraping', 'research', 'planning', 'coding'].map((skill, index) => (
            <motion.button
              key={skill}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                setSelectedSkills((prev) =>
                  prev.includes(skill)
                    ? prev.filter((s) => s !== skill)
                    : [...prev, skill]
                );
              }}
              className={`px-3 py-1 rounded-full text-sm transition-all ${
                selectedSkills.includes(skill)
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300'
              }`}
            >
              {skill}
            </motion.button>
          ))}
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleSearch}
          disabled={loading}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 hover:shadow-xl transition-all disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Find Compatible Partners'}
        </motion.button>
      </div>

      {/* Results */}
      <AnimatePresence mode="wait">
        {candidates.length === 0 && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="text-center py-12 text-slate-500"
          >
            <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Start searching to discover compatible agents</p>
          </motion.div>
        )}

        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {[1, 2, 3, 4].map((i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                className="h-48 bg-slate-100 dark:bg-slate-700 rounded-lg animate-pulse"
              />
            ))}
          </motion.div>
        )}

        {!loading && candidates.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {candidates.map((candidate, index) => {
              const hasRequested = requestedMatches.has(candidate.agent.agent_id);
              return (
                <motion.div
                  key={candidate.agent.agent_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative"
                >
                  <AgentCard
                    agent={candidate.agent}
                    compatibility={candidate.compatibility}
                    matchingSkills={candidate.matching_skills}
                    complementarySkills={candidate.complementary_skills}
                    onMatch={hasRequested ? undefined : () => handleMatch(candidate.agent.agent_id)}
                  />
                  <AnimatePresence>
                    {hasRequested && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        className="absolute top-4 right-4 bg-green-600 text-white px-3 py-1 rounded-full text-sm flex items-center gap-1 shadow-lg"
                      >
                        <Check className="w-4 h-4" />
                        Request Sent
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
