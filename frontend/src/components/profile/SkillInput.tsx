"use client";

import { useState, KeyboardEvent } from "react";
import { X, Plus } from "lucide-react";
import { Badge } from "@/components/ui";

interface SkillInputProps {
  skills: string[];
  onChange: (skills: string[]) => void;
  suggestions?: string[];
  maxSkills?: number;
}

const defaultSuggestions = [
  "python",
  "javascript",
  "typescript",
  "react",
  "node.js",
  "data-analysis",
  "machine-learning",
  "web-scraping",
  "research",
  "writing",
  "debugging",
  "testing",
  "devops",
  "design",
  "ui-ux",
];

export function SkillInput({
  skills,
  onChange,
  suggestions = defaultSuggestions,
  maxSkills = 15,
}: SkillInputProps) {
  const [input, setInput] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);

  const filteredSuggestions = suggestions.filter(
    (s) =>
      s.toLowerCase().includes(input.toLowerCase()) &&
      !skills.includes(s)
  );

  const addSkill = (skill: string) => {
    const normalized = skill.toLowerCase().trim();
    if (normalized && !skills.includes(normalized) && skills.length < maxSkills) {
      onChange([...skills, normalized]);
      setInput("");
    }
  };

  const removeSkill = (skill: string) => {
    onChange(skills.filter((s) => s !== skill));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addSkill(input);
    } else if (e.key === "Backspace" && !input && skills.length > 0) {
      removeSkill(skills[skills.length - 1]);
    }
  };

  return (
    <div className="space-y-3">
      {/* Selected Skills */}
      {skills.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {skills.map((skill) => (
            <Badge key={skill} variant="orange" className="group">
              {skill}
              <button
                type="button"
                onClick={() => removeSkill(skill)}
                className="ml-1.5 opacity-70 hover:opacity-100"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setShowSuggestions(true);
          }}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder={
            skills.length >= maxSkills
              ? `Maximum ${maxSkills} skills reached`
              : "Type a skill and press Enter..."
          }
          disabled={skills.length >= maxSkills}
          className="w-full rounded-lg border border-border bg-zinc-800 px-4 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:cursor-not-allowed disabled:opacity-50"
        />

        {/* Suggestions Dropdown */}
        {showSuggestions && input && filteredSuggestions.length > 0 && (
          <div className="absolute z-10 mt-1 w-full rounded-lg border border-border bg-zinc-800 py-2 shadow-lg">
            {filteredSuggestions.slice(0, 8).map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => addSkill(suggestion)}
                className="flex w-full items-center gap-2 px-4 py-2 text-sm hover:bg-zinc-700"
              >
                <Plus className="h-3 w-3 text-muted-foreground" />
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      <p className="text-xs text-muted-foreground">
        {skills.length}/{maxSkills} skills • Press Enter to add
      </p>
    </div>
  );
}
