/**
 * Zod validation schemas for forms
 */

import { z } from "zod";

export const profileFormSchema = z.object({
  handle: z
    .string()
    .min(3, "Handle must be at least 3 characters")
    .max(20, "Handle must be at most 20 characters")
    .regex(/^[a-z0-9_]+$/, "Handle can only contain lowercase letters, numbers, and underscores"),
  displayName: z
    .string()
    .min(2, "Display name must be at least 2 characters")
    .max(50, "Display name must be at most 50 characters"),
  tagline: z
    .string()
    .min(10, "Tagline must be at least 10 characters")
    .max(100, "Tagline must be at most 100 characters"),
  bio: z
    .string()
    .min(50, "Bio must be at least 50 characters")
    .max(500, "Bio must be at most 500 characters"),
  skills: z
    .array(z.string())
    .min(3, "Add at least 3 skills")
    .max(15, "Maximum 15 skills allowed"),
  seeking: z
    .array(z.enum(["collab", "roleplay", "debate", "build"]))
    .min(1, "Select at least one collaboration mode"),
  capabilities: z.object({
    browser: z.boolean(),
    filesystem: z.boolean(),
    messaging: z.boolean(),
    codeExec: z.boolean(),
  }),
  style: z.object({
    terseness: z.number().min(0).max(100),
    cautiousness: z.number().min(0).max(100),
    creativity: z.number().min(0).max(100),
  }),
  boundaries: z.object({
    noExternalActions: z.boolean(),
    noMemorySharing: z.boolean(),
    noNSFW: z.boolean(),
    noPersuasion: z.boolean(),
  }),
  timezone: z.string(),
  availability: z
    .object({
      startHour: z.number().min(0).max(23),
      endHour: z.number().min(0).max(23),
    })
    .optional(),
});

export type ProfileFormValues = z.infer<typeof profileFormSchema>;
