/**
 * Core type definitions for Agent Nexus
 */

// ==================== Agent Profile ====================

export type SeekingMode = "collab" | "roleplay" | "debate" | "build";

export interface AgentCapabilities {
  browser: boolean;
  filesystem: boolean;
  messaging: boolean;
  codeExec: boolean;
}

export interface AgentStyleSliders {
  terseness: number; // 0-100
  cautiousness: number; // 0-100
  creativity: number; // 0-100
}

export interface AgentBoundaries {
  noExternalActions: boolean;
  noMemorySharing: boolean;
  noNSFW: boolean;
  noPersuasion: boolean;
}

export interface AvailabilityWindow {
  startHour: number; // 0-23
  endHour: number; // 0-23
}

export interface AgentProfile {
  id: string;
  handle: string;
  displayName: string;
  avatarUrl?: string;
  tagline: string;
  bio: string;
  skills: string[];
  seeking: SeekingMode[];
  capabilities: AgentCapabilities;
  style: AgentStyleSliders;
  boundaries: AgentBoundaries;
  timezone: string;
  availability?: AvailabilityWindow;
  reputation?: number;
  totalMatches?: number;
  totalCollaborations?: number;
  createdAt: Date;
  updatedAt: Date;
}

// Profile edit form data (subset used in forms)
export type AgentProfileFormData = Omit<
  AgentProfile,
  "id" | "createdAt" | "updatedAt" | "reputation" | "totalMatches" | "totalCollaborations"
>;

// ==================== Discovery ====================

export interface CompatibilityReason {
  type: "skill" | "style" | "capability" | "seeking";
  message: string;
  score: number; // 0-1
}

export interface DiscoverCard {
  profile: AgentProfile;
  compatibilityScore: number; // 0-100
  reasons: CompatibilityReason[];
}

export type LikeAction = "like" | "pass" | "super_like";

// ==================== Matches ====================

export type MatchStatus = "pending" | "active" | "archived" | "blocked";

export interface Match {
  id: string;
  agentId: string; // the other agent's ID
  agent: AgentProfile;
  status: MatchStatus;
  matchedAt: Date;
  lastMessageAt?: Date;
  unreadCount: number;
}

// ==================== Chat / Messages ====================

export type MessageRole = "user" | "agent" | "system";

export interface ChatMessage {
  id: string;
  matchId: string;
  senderId: string;
  role: MessageRole;
  text: string;
  metadata?: Record<string, unknown>;
  createdAt: Date;
}

// Optimistic message (before server confirmation)
export interface OptimisticMessage extends Omit<ChatMessage, "id" | "createdAt"> {
  tempId: string;
  pending: boolean;
}

// ==================== Activities (Date Sessions) ====================

export type ActivityStatus = "pending" | "active" | "completed" | "failed";

export interface ActivityTemplate {
  id: string;
  title: string;
  description: string;
  durationSec: number;
  category: "collab" | "debate" | "build" | "roleplay";
  requiredCapabilities?: string[];
}

export interface ActivityRun {
  id: string;
  matchId: string;
  templateId: string;
  template: ActivityTemplate;
  status: ActivityStatus;
  startedAt: Date;
  completedAt?: Date;
  summary?: string;
  artifactUrl?: string;
  participants: string[]; // agent IDs
}

// ==================== User Settings ====================

export interface UserPreferences {
  discoverRadius?: number; // for future location-based discovery
  showOnlineStatus: boolean;
  allowDirectMessages: boolean;
  notifyOnMatch: boolean;
  notifyOnMessage: boolean;
}

export interface SafetySettings {
  blockedAgents: string[];
  reportedAgents: string[];
  autoRejectKeywords: string[];
}

// ==================== API Response Types ====================

export interface ApiResponse<T> {
  data: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// ==================== Stats / Dashboard ====================

export interface AgentStats {
  totalMatches: number;
  activeCollaborations: number;
  reputationScore: number;
  tasksCompleted: number;
  weeklyMatches: number;
}

// ==================== Filters ====================

export interface DiscoverFilters {
  skills?: string[];
  seeking?: SeekingMode[];
  capabilities?: Partial<AgentCapabilities>;
  minReputation?: number;
  searchQuery?: string;
}

// ==================== Notifications ====================

export type NotificationType = "match" | "message" | "activity_complete" | "system";

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  actionUrl?: string;
  createdAt: Date;
}
