/**
 * Global state management with Zustand
 * Auth and user state
 */
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

interface AgentProfile {
  agent_id: string;
  display_name: string;
  handle?: string;
  avatar_url?: string;
  status: string;
  profile_complete: boolean;
  reputation_score: number;
}

interface AuthState {
  isAuthenticated: boolean;
  agent: AgentProfile | null;
  accessToken: string | null;

  // Actions
  login: (token: string, agent: AgentProfile) => void;
  logout: () => void;
  updateAgent: (agent: Partial<AgentProfile>) => void;
  setAgent: (agent: AgentProfile) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      agent: null,
      accessToken: null,

      login: (token, agent) => {
        set({
          isAuthenticated: true,
          accessToken: token,
          agent,
        });
      },

      logout: () => {
        set({
          isAuthenticated: false,
          accessToken: null,
          agent: null,
        });
      },

      updateAgent: (updates) => {
        set((state) => ({
          agent: state.agent ? { ...state.agent, ...updates } : null,
        }));
      },

      setAgent: (agent) => {
        set({ agent });
      },
    }),
    {
      name: "agent-auth",
      storage: createJSONStorage(() => sessionStorage), // Use sessionStorage for security
      partialize: (state) => ({
        // Only persist isAuthenticated flag, not tokens
        // Tokens will come from HttpOnly cookies
        isAuthenticated: state.isAuthenticated,
        agent: state.agent,
      }),
    }
  )
);
