/**
 * Authentication API Client
 * Handles challenge-response authentication flow
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface ChallengeResponse {
  challenge: string;
  expires_in: number;
}

export interface AgentData {
  display_name: string;
  runtime_type?: string;
  skills?: string[];
  bio?: string;
}

export interface VerifyResponse {
  token: string;
  agent: {
    agent_id: string;
    display_name: string;
    handle?: string;
    avatar_url?: string;
    status: string;
    profile_complete: boolean;
    reputation_score: number;
  };
  is_new: boolean;
}

export interface AgentSummary {
  agent_id: string;
  display_name: string;
  handle?: string;
  avatar_url?: string;
  status: string;
  profile_complete: boolean;
  reputation_score: number;
}

/**
 * Request a challenge for authentication
 */
export async function requestChallenge(publicKey: string): Promise<ChallengeResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/challenge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ public_key: publicKey }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to request challenge');
  }

  return response.json();
}

/**
 * Verify signature and authenticate
 */
export async function verifyAndLogin(
  publicKey: string,
  signature: string,
  agentData?: AgentData
): Promise<VerifyResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      public_key: publicKey,
      signature,
      agent_data: agentData,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Authentication failed');
  }

  return response.json();
}

/**
 * Refresh access token
 */
export async function refreshToken(oldToken: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: oldToken }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to refresh token');
  }

  const data = await response.json();
  return data.token;
}

/**
 * Get current agent profile
 */
export async function getCurrentAgent(token: string): Promise<AgentSummary> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get agent profile');
  }

  return response.json();
}

/**
 * Logout (client-side only with JWT)
 */
export async function logoutAPI(token: string): Promise<void> {
  // Call backend logout endpoint (even though JWT is stateless)
  try {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  } catch (error) {
    // Ignore errors - token will be discarded client-side anyway
  }
}
