/**
 * Theme tokens and constants for Agent Nexus
 * Provides consistent colors, gradients, and design tokens across the app
 */

export const theme = {
  // Primary accent color (orange)
  accent: {
    primary: "hsl(24, 100%, 55%)", // #f97316
    primaryDark: "hsl(24, 100%, 45%)",
    primaryLight: "hsl(24, 100%, 65%)",
  },

  // Avatar gradient classes
  avatarGradients: [
    "avatar-gradient-1",
    "avatar-gradient-2",
    "avatar-gradient-3",
    "avatar-gradient-4",
  ] as const,

  // Badge variants
  badges: {
    orange: "badge-orange",
    green: "badge-green",
    blue: "badge-blue",
    purple: "badge-purple",
  } as const,

  // Status colors
  status: {
    online: "bg-green-500",
    offline: "bg-zinc-600",
    busy: "bg-orange-500",
    away: "bg-yellow-500",
  } as const,
} as const;

/**
 * Get a random avatar gradient class
 */
export function getRandomAvatarGradient(): string {
  const gradients = theme.avatarGradients;
  return gradients[Math.floor(Math.random() * gradients.length)];
}

/**
 * Get avatar gradient by index (for consistent avatars)
 */
export function getAvatarGradient(index: number): string {
  const gradients = theme.avatarGradients;
  return gradients[index % gradients.length];
}

/**
 * Get initials from name for avatar
 */
export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}
