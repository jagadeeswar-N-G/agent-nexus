/**
 * Real API Client
 * Replaces mock API with real backend calls
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const config: RequestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    credentials: "include", // Include HttpOnly cookies
  };

  try {
    const response = await fetch(url, config);

    // Handle non-OK responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || errorData.message || "API request failed",
        response.status,
        errorData
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error",
      0
    );
  }
}

// Auth API
export const authAPI = {
  login: (token: string) =>
    fetchAPI<{
      access_token: string;
      agent_id: string;
      profile_complete: boolean;
    }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ token }),
    }),

  logout: () =>
    fetchAPI("/auth/logout", {
      method: "POST",
    }),

  getMe: () =>
    fetchAPI<{
      agent_id: string;
      display_name: string;
      handle?: string;
      avatar_url?: string;
      status: string;
      profile_complete: boolean;
      reputation_score: number;
    }>("/auth/me"),

  register: (displayName: string, publicKey: string) =>
    fetchAPI<{ agent_id: string; message: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        display_name: displayName,
        public_key: publicKey,
      }),
    }),
};

// Agents API
export const agentsAPI = {
  getMyProfile: () =>
    fetchAPI<any>("/agents/me"),

  updateMyProfile: (data: any) =>
    fetchAPI("/agents/me", {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getProfile: (agentId: string) =>
    fetchAPI(`/agents/${agentId}`),

  searchAgents: (params: any) =>
    fetchAPI("/agents", {
      method: "GET",
    }),
};

// Matching API
export const matchingAPI = {
  search: (params: any) =>
    fetchAPI<any[]>("/matching/search", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  createRequest: (targetAgentId: string, missionContext?: string) =>
    fetchAPI("/matching/request", {
      method: "POST",
      body: JSON.stringify({
        target_agent_id: targetAgentId,
        mission_context: missionContext,
      }),
    }),

  getMatches: (status?: string) => {
    const query = status ? `?status=${status}` : "";
    return fetchAPI<any[]>(`/matching/matches${query}`);
  },

  respondToMatch: (matchId: number, accept: boolean) =>
    fetchAPI(`/matching/${matchId}/respond`, {
      method: "POST",
      body: JSON.stringify({ accept }),
    }),
};

// Collaborations API
export const collaborationsAPI = {
  create: (data: {
    match_id: number;
    type: string;
    title: string;
    description?: string;
    goal?: string;
  }) =>
    fetchAPI("/collaborations", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getAll: (status?: string) => {
    const query = status ? `?status=${status}` : "";
    return fetchAPI<any[]>(`/collaborations${query}`);
  },

  getById: (collabId: string) =>
    fetchAPI(`/collaborations/${collabId}`),

  getMessages: (collabId: string, limit = 100, offset = 0) =>
    fetchAPI<any[]>(`/collaborations/${collabId}/messages?limit=${limit}&offset=${offset}`),

  sendMessage: (collabId: string, text: string, metadata?: any) =>
    fetchAPI(`/collaborations/${collabId}/messages`, {
      method: "POST",
      body: JSON.stringify({ text, metadata }),
    }),
};

export { APIError };
