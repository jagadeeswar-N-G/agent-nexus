/**
 * API client for Agent Nexus
 * Supports mock mode via NEXT_PUBLIC_USE_MOCKS=true
 */

import type {
  AgentProfile,
  AgentProfileFormData,
  DiscoverCard,
  DiscoverFilters,
  Match,
  ChatMessage,
  ActivityTemplate,
  ActivityRun,
  AgentStats,
  Notification,
  LikeAction,
  ApiResponse,
  PaginatedResponse,
} from "./types";

import {
  mockCurrentUser,
  mockDiscoverCards,
  mockMatches,
  mockMessages,
  mockActivityTemplates,
  mockActivityRuns,
  mockStats,
  mockNotifications,
  delay,
  getRandomAgents,
  generateMockCompatibility,
} from "./mocks";

// Feature flag for using mocks
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === "true";
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// ==================== Helper Functions ====================

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return {
      data: null as T,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

// ==================== Profile API ====================

export async function getCurrentProfile(): Promise<ApiResponse<AgentProfile>> {
  if (USE_MOCKS) {
    await delay(300);
    return { data: mockCurrentUser };
  }

  return fetchApi<AgentProfile>("/profile/me");
}

export async function updateProfile(
  data: Partial<AgentProfileFormData>
): Promise<ApiResponse<AgentProfile>> {
  if (USE_MOCKS) {
    await delay(500);
    return {
      data: {
        ...mockCurrentUser,
        ...data,
        updatedAt: new Date(),
      },
    };
  }

  return fetchApi<AgentProfile>("/profile/me", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// ==================== Discovery API ====================

export async function getDiscoverCards(
  filters?: DiscoverFilters,
  page: number = 1,
  pageSize: number = 20
): Promise<ApiResponse<PaginatedResponse<DiscoverCard>>> {
  if (USE_MOCKS) {
    await delay(400);

    // Simple filtering for mocks
    let cards = mockDiscoverCards;

    if (filters?.skills && filters.skills.length > 0) {
      cards = cards.filter((card) =>
        filters.skills!.some((skill) => card.profile.skills.includes(skill))
      );
    }

    if (filters?.seeking && filters.seeking.length > 0) {
      cards = cards.filter((card) =>
        filters.seeking!.some((mode) => card.profile.seeking.includes(mode))
      );
    }

    // Generate more cards if needed
    if (cards.length < pageSize) {
      const moreAgents = getRandomAgents(pageSize - cards.length);
      const moreCards = moreAgents.map(generateMockCompatibility);
      cards = [...cards, ...moreCards];
    }

    return {
      data: {
        data: cards.slice(0, pageSize),
        total: cards.length,
        page,
        pageSize,
        hasMore: cards.length > pageSize,
      },
    };
  }

  return fetchApi<PaginatedResponse<DiscoverCard>>(
    `/discover?page=${page}&pageSize=${pageSize}`,
    {
      method: "POST",
      body: JSON.stringify(filters || {}),
    }
  );
}

export async function submitLikeAction(
  agentId: string,
  action: LikeAction
): Promise<ApiResponse<{ matched: boolean; matchId?: string }>> {
  if (USE_MOCKS) {
    await delay(300);

    // Simulate 30% match rate on likes
    const matched = action === "like" && Math.random() > 0.7;

    return {
      data: {
        matched,
        matchId: matched ? `match-new-${Date.now()}` : undefined,
      },
    };
  }

  return fetchApi<{ matched: boolean; matchId?: string }>(`/discover/${agentId}/action`, {
    method: "POST",
    body: JSON.stringify({ action }),
  });
}

// ==================== Matches API ====================

export async function getMatches(): Promise<ApiResponse<Match[]>> {
  if (USE_MOCKS) {
    await delay(300);
    return { data: mockMatches };
  }

  return fetchApi<Match[]>("/matches");
}

export async function getMatchById(matchId: string): Promise<ApiResponse<Match>> {
  if (USE_MOCKS) {
    await delay(200);
    const match = mockMatches.find((m) => m.id === matchId);

    if (!match) {
      return { data: null as unknown as Match, error: "Match not found" };
    }

    return { data: match };
  }

  return fetchApi<Match>(`/matches/${matchId}`);
}

// ==================== Chat API ====================

export async function getMessages(matchId: string): Promise<ApiResponse<ChatMessage[]>> {
  if (USE_MOCKS) {
    await delay(300);
    return { data: mockMessages[matchId] || [] };
  }

  return fetchApi<ChatMessage[]>(`/matches/${matchId}/messages`);
}

export async function sendMessage(
  matchId: string,
  text: string
): Promise<ApiResponse<ChatMessage>> {
  if (USE_MOCKS) {
    await delay(500);

    const newMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      matchId,
      senderId: mockCurrentUser.id,
      role: "user",
      text,
      createdAt: new Date(),
    };

    // Add to mock messages
    if (!mockMessages[matchId]) {
      mockMessages[matchId] = [];
    }
    mockMessages[matchId].push(newMessage);

    return { data: newMessage };
  }

  return fetchApi<ChatMessage>(`/matches/${matchId}/messages`, {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

// ==================== Activities API ====================

export async function getActivityTemplates(): Promise<ApiResponse<ActivityTemplate[]>> {
  if (USE_MOCKS) {
    await delay(200);
    return { data: mockActivityTemplates };
  }

  return fetchApi<ActivityTemplate[]>("/activities/templates");
}

export async function startActivity(
  matchId: string,
  templateId: string
): Promise<ApiResponse<ActivityRun>> {
  if (USE_MOCKS) {
    await delay(400);

    const template = mockActivityTemplates.find((t) => t.id === templateId);

    if (!template) {
      return { data: null as unknown as ActivityRun, error: "Template not found" };
    }

    const newRun: ActivityRun = {
      id: `run-${Date.now()}`,
      matchId,
      templateId,
      template,
      status: "active",
      startedAt: new Date(),
      participants: [mockCurrentUser.id, matchId],
    };

    return { data: newRun };
  }

  return fetchApi<ActivityRun>("/activities/start", {
    method: "POST",
    body: JSON.stringify({ matchId, templateId }),
  });
}

export async function getActivityRuns(): Promise<ApiResponse<ActivityRun[]>> {
  if (USE_MOCKS) {
    await delay(300);
    return { data: mockActivityRuns };
  }

  return fetchApi<ActivityRun[]>("/activities/runs");
}

// ==================== Stats API ====================

export async function getStats(): Promise<ApiResponse<AgentStats>> {
  if (USE_MOCKS) {
    await delay(200);
    return { data: mockStats };
  }

  return fetchApi<AgentStats>("/stats");
}

// ==================== Notifications API ====================

export async function getNotifications(): Promise<ApiResponse<Notification[]>> {
  if (USE_MOCKS) {
    await delay(200);
    return { data: mockNotifications };
  }

  return fetchApi<Notification[]>("/notifications");
}

export async function markNotificationRead(
  notificationId: string
): Promise<ApiResponse<void>> {
  if (USE_MOCKS) {
    await delay(100);
    const notif = mockNotifications.find((n) => n.id === notificationId);
    if (notif) {
      notif.read = true;
    }
    return { data: undefined };
  }

  return fetchApi<void>(`/notifications/${notificationId}/read`, {
    method: "POST",
  });
}
