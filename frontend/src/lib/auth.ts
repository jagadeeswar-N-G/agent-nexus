/**
 * Authentication utilities
 * Token management and auth state
 */

const TOKEN_KEY = 'agent_auth_token';
const KEYPAIR_KEY = 'agent_keypair'; // For demo mode only

export interface AgentProfile {
  agent_id: string;
  display_name: string;
  handle?: string;
  avatar_url?: string;
  status: string;
  profile_complete: boolean;
  reputation_score: number;
}

/**
 * Save JWT token to localStorage
 */
export function saveToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Get JWT token from localStorage
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Remove token from localStorage
 */
export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const token = getToken();
  if (!token) return false;

  try {
    // Decode JWT to check expiration
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    return Date.now() < exp;
  } catch (error) {
    return false;
  }
}

/**
 * Save keypair to localStorage (DEMO MODE ONLY - not secure!)
 */
export function saveKeypair(publicKey: string, privateKey: string): void {
  localStorage.setItem(KEYPAIR_KEY, JSON.stringify({ publicKey, privateKey }));
}

/**
 * Get saved keypair from localStorage
 */
export function getSavedKeypair(): { publicKey: string; privateKey: string } | null {
  const data = localStorage.getItem(KEYPAIR_KEY);
  if (!data) return null;

  try {
    return JSON.parse(data);
  } catch (error) {
    return null;
  }
}

/**
 * Clear saved keypair
 */
export function clearKeypair(): void {
  localStorage.removeItem(KEYPAIR_KEY);
}

/**
 * Clear all auth data
 */
export function logout(): void {
  clearToken();
  // Don't clear keypair - user might want to login again
}
