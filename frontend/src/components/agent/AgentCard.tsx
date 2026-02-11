"use client";

interface Agent {
  id: string;
  display_name: string;
  handle?: string;
  avatar_url?: string;
  bio?: string;
  skills: string[];
  reputation_score?: number;
  is_online?: boolean;
}

interface AgentCardProps {
  agent: Agent;
  onConnect?: (agentId: string) => void;
}

export function AgentCard({ agent, onConnect }: AgentCardProps) {
  return (
    <div className="rounded-lg border bg-card p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
          {agent.display_name.charAt(0).toUpperCase()}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-lg truncate">{agent.display_name}</h3>
            {agent.is_online && (
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
            )}
          </div>

          {agent.handle && (
            <p className="text-sm text-muted-foreground">@{agent.handle}</p>
          )}

          {agent.bio && (
            <p className="text-sm mt-2 line-clamp-2">{agent.bio}</p>
          )}

          <div className="flex flex-wrap gap-1 mt-3">
            {agent.skills.slice(0, 3).map((skill) => (
              <span
                key={skill}
                className="px-2 py-1 text-xs rounded-full bg-primary/10 text-primary"
              >
                {skill}
              </span>
            ))}
            {agent.skills.length > 3 && (
              <span className="px-2 py-1 text-xs rounded-full bg-muted text-muted-foreground">
                +{agent.skills.length - 3}
              </span>
            )}
          </div>

          {agent.reputation_score !== undefined && (
            <div className="mt-3 text-sm text-muted-foreground">
              Reputation: {agent.reputation_score.toFixed(1)}
            </div>
          )}

          {onConnect && (
            <button
              onClick={() => onConnect(agent.id)}
              className="mt-4 w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Connect
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
