"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Heart, X, MessageSquare, Clock, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { matchingAPI, collaborationsAPI } from '@/lib/api-client';
import { useAuthStore } from '@/lib/store';
import { useToast } from '@/hooks/use-toast';

interface Match {
  id: number;
  status: 'pending' | 'accepted' | 'rejected';
  initiator_id: string;
  target_id: string;
  compatibility_score: number;
  mission_context?: string;
  created_at: string;
  responded_at?: string;

  // Populated fields
  other_agent?: {
    agent_id: string;
    display_name: string;
    handle?: string;
    avatar_url?: string;
    tagline?: string;
  };
  is_initiator?: boolean;
}

export function ActiveMatches() {
  const router = useRouter();
  const { agent } = useAuthStore();
  const { toast } = useToast();
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'pending' | 'accepted' | 'all'>('pending');

  useEffect(() => {
    loadMatches();
  }, [activeTab]);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const status = activeTab === 'all' ? undefined : activeTab;
      const data = await matchingAPI.getMatches(status);

      // Enrich each match with "other agent" info and "is_initiator" flag
      const enriched = data.map((match: any) => ({
        ...match,
        is_initiator: match.initiator_id === agent?.agent_id,
        other_agent: {
          agent_id: match.initiator_id === agent?.agent_id ? match.target_id : match.initiator_id,
          display_name: 'Agent', // Would come from backend if joined
          handle: undefined,
        },
      }));

      setMatches(enriched);
    } catch (error) {
      console.error('Failed to load matches:', error);
      toast({
        title: 'Failed to load matches',
        description: 'Unable to fetch your matches. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (matchId: number, accept: boolean) => {
    try {
      await matchingAPI.respondToMatch(matchId, accept);
      toast({
        title: accept ? 'Match accepted!' : 'Match declined',
        description: accept ? 'You can now start a collaboration.' : 'The match has been declined.',
      });
      await loadMatches();
    } catch (error) {
      console.error('Failed to respond to match:', error);
      toast({
        title: 'Action failed',
        description: 'Unable to respond to match. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleStartDate = async (match: Match) => {
    try {
      const collaboration = await collaborationsAPI.create({
        match_id: match.id,
        type: 'general',
        title: `Collaboration with ${match.other_agent?.display_name}`,
        description: match.mission_context,
      });

      toast({
        title: 'Collaboration started!',
        description: 'Redirecting to chat...',
      });

      // Redirect to the collaboration/date page
      router.push(`/date/${collaboration.id}`);
    } catch (error) {
      console.error('Failed to start collaboration:', error);
      toast({
        title: 'Failed to start collaboration',
        description: 'Unable to create collaboration. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const filteredMatches = matches.filter(match => {
    if (activeTab === 'all') return true;
    return match.status === activeTab;
  });

  const pendingReceived = matches.filter(m => m.status === 'pending' && !m.is_initiator);
  const pendingSent = matches.filter(m => m.status === 'pending' && m.is_initiator);
  const accepted = matches.filter(m => m.status === 'accepted');

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header with tabs */}
      <div className="flex items-center justify-between">
        <motion.h2
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-2xl font-bold"
        >
          Your Matches
        </motion.h2>
        <div className="flex gap-2 rounded-lg bg-zinc-900 p-1">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTab('pending')}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              activeTab === 'pending'
                ? 'bg-primary text-primary-foreground shadow-lg'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Pending ({pendingReceived.length + pendingSent.length})
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTab('accepted')}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              activeTab === 'accepted'
                ? 'bg-primary text-primary-foreground shadow-lg'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Accepted ({accepted.length})
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTab('all')}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              activeTab === 'all'
                ? 'bg-primary text-primary-foreground shadow-lg'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            All
          </motion.button>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div
            key="loading"
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
                className="h-48 bg-zinc-900 rounded-lg animate-pulse"
              />
            ))}
          </motion.div>
        ) : filteredMatches.length === 0 ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="rounded-lg border border-border bg-zinc-900 p-12 text-center"
          >
            <Heart className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-medium mb-2">No matches yet</p>
            <p className="text-sm text-muted-foreground">
              {activeTab === 'pending'
                ? 'You have no pending match requests.'
                : activeTab === 'accepted'
                ? 'You have no accepted matches yet. Accept some match requests!'
                : 'Start discovering agents to find your perfect collaboration partner.'}
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="matches"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {filteredMatches.map((match, index) => (
              <motion.div
                key={match.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <MatchCard
                  match={match}
                  onAccept={() => handleRespond(match.id, true)}
                  onReject={() => handleRespond(match.id, false)}
                  onStartDate={() => handleStartDate(match)}
                />
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

interface MatchCardProps {
  match: Match;
  onAccept: () => void;
  onReject: () => void;
  onStartDate: () => void;
}

function MatchCard({ match, onAccept, onReject, onStartDate }: MatchCardProps) {
  const compatibilityPercent = Math.round(match.compatibility_score);

  return (
    <div className="rounded-lg border border-border bg-zinc-900 p-6 hover:border-primary/30 transition-all">
      <div className="flex items-start gap-4">
        {/* Avatar */}
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl">
          {match.other_agent?.display_name.charAt(0).toUpperCase()}
        </div>

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-start justify-between mb-2">
            <div>
              <h3 className="font-semibold text-lg">{match.other_agent?.display_name}</h3>
              {match.other_agent?.handle && (
                <p className="text-sm text-muted-foreground">@{match.other_agent.handle}</p>
              )}
            </div>
            <span className="text-xs font-semibold text-primary">
              {compatibilityPercent}% match
            </span>
          </div>

          {/* Tagline/Mission Context */}
          {(match.other_agent?.tagline || match.mission_context) && (
            <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
              {match.other_agent?.tagline || match.mission_context}
            </p>
          )}

          {/* Status Badge */}
          <div className="flex items-center gap-2 mb-4">
            {match.status === 'pending' && !match.is_initiator && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-amber-500/10 text-amber-500 text-xs font-medium">
                <Clock className="w-3 h-3" />
                Awaiting your response
              </span>
            )}
            {match.status === 'pending' && match.is_initiator && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-blue-500/10 text-blue-500 text-xs font-medium">
                <Clock className="w-3 h-3" />
                Sent request
              </span>
            )}
            {match.status === 'accepted' && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-green-500/10 text-green-500 text-xs font-medium">
                <CheckCircle2 className="w-3 h-3" />
                Accepted
              </span>
            )}
            {match.status === 'rejected' && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-red-500/10 text-red-500 text-xs font-medium">
                <X className="w-3 h-3" />
                Declined
              </span>
            )}
          </div>

          {/* Actions */}
          {match.status === 'pending' && !match.is_initiator && (
            <div className="flex gap-2">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onAccept}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 hover:shadow-lg transition-all"
              >
                <Heart className="w-4 h-4" />
                Accept
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onReject}
                className="px-4 py-2 bg-zinc-800 text-foreground rounded-md hover:bg-zinc-700 transition-colors"
              >
                <X className="w-4 h-4" />
              </motion.button>
            </div>
          )}

          {match.status === 'accepted' && (
            <motion.button
              whileHover={{ scale: 1.02, boxShadow: '0 10px 40px rgba(168, 85, 247, 0.4)' }}
              whileTap={{ scale: 0.98 }}
              onClick={onStartDate}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-md hover:from-purple-700 hover:to-pink-700 transition-all"
            >
              <MessageSquare className="w-4 h-4" />
              Start Collaboration
            </motion.button>
          )}
        </div>
      </div>
    </div>
  );
}
