"use client";

interface Agent {
  id: string;
  agent_id?: string;
  display_name: string;
  handle?: string;
  avatar_url?: string;
  tagline?: string;
  bio?: string;
  skills: string[];
  reputation_score?: number;
  is_online?: boolean;
}

interface CompatibilityScore {
  overall: number; // 0..1
  skill_match?: number;
  style_match?: number;
  goal_alignment?: number;
  explanation?: string;
}

interface AgentCardProps {
  agent: Agent;

  // Used by DiscoverAgents
  compatibility?: CompatibilityScore;
  matchingSkills?: string[];
  complementarySkills?: string[];
  onMatch?: () => void | Promise<void>;

  // Back-compat (used elsewhere)
  onConnect?: (agentId: string) => void;
}

export function AgentCard({
  agent,
  compatibility,
  matchingSkills,
  complementarySkills,
  onMatch,
  onConnect,
}: AgentCardProps) {
  const overallPct =
    compatibility && Number.isFinite(compatibility.overall)
      ? Math.round(compatibility.overall * 100)
      : null;

  const displayHandle = agent.handle ?? agent.agent_id;

  return (
    <div className="rounded-lg border border-border bg-zinc-900 p-4 hover:border-primary/30 hover:shadow-lg transition-all">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
          {agent.display_name.charAt(0).toUpperCase()}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-lg truncate">{agent.display_name}</h3>
            {agent.is_online && <span className="w-2 h-2 rounded-full bg-green-500" />}
            {overallPct !== null && (
              <span className="ml-auto text-xs font-semibold text-primary">
                {overallPct}% match
              </span>
            )}
          </div>

          {displayHandle && (
            <p className="text-sm text-muted-foreground">@{displayHandle}</p>
          )}

          {agent.tagline && (
            <p className="mt-2 text-sm text-foreground/90 line-clamp-1">
              {agent.tagline}
            </p>
          )}

          {agent.bio && (
            <p className="text-sm mt-2 text-muted-foreground line-clamp-2">
              {agent.bio}
            </p>
          )}

          <div className="flex flex-wrap gap-1 mt-3">
            {agent.skills.slice(0, 4).map((skill) => (
              <span
                key={skill}
                className="px-2 py-1 text-xs rounded-full bg-primary/10 text-primary"
              >
                {skill}
              </span>
            ))}
            {agent.skills.length > 4 && (
              <span className="px-2 py-1 text-xs rounded-full bg-zinc-800 text-muted-foreground">
                +{agent.skills.length - 4}
              </span>
            )}
          </div>

          {(matchingSkills?.length || complementarySkills?.length) ? (
            <div className="mt-3 space-y-1 text-xs text-muted-foreground">
              {matchingSkills?.length ? (
                <p>
                  <span className="font-medium text-foreground/80">Matching:</span>{" "}
                  {matchingSkills.slice(0, 4).join(", ")}
                </p>
              ) : null}
              {complementarySkills?.length ? (
                <p>
                  <span className="font-medium text-foreground/80">Complementary:</span>{" "}
                  {complementarySkills.slice(0, 4).join(", ")}
                </p>
              ) : null}
            </div>
          ) : null}

          {agent.reputation_score !== undefined && (
            <div className="mt-3 text-sm text-muted-foreground">
              Reputation: {agent.reputation_score.toFixed(1)}
            </div>
          )}

          {onMatch ? (
            <button
              onClick={() => onMatch()}
              className="mt-4 w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Request Match
            </button>
          ) : onConnect ? (
            <button
              onClick={() => onConnect(agent.id)}
              className="mt-4 w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Connect
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
